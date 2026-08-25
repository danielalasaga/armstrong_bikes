"""Grader registry for the bike-sourcing eval suite.

Mirrors the pattern in day2/01_evals/Building_an_Eval.ipynb: every grader is
`fn(result, check, context=None) -> {"score": 0.0|1.0, "reason": str}`, looked
up by name in GRADER_REGISTRY, and a task passes only if every check from
every grader it declares scores 1.0.

`response_contains`, `response_numeric`, and `llm_judge` are carried over
almost verbatim from that notebook — they still work fine for grading the
free-text portions of a sourcing memo. What's new here is a family of graders
for structured JSON output, because these agents return a parts list / cost
breakdown / risk assessment as data, not a chat reply:

  - json_field_equals      exact match on a dotted path into result["output"]
  - json_field_tolerance    numeric match within an absolute or %-tolerance
  - list_field_match        set-compare a list field against expected values
  - schema_required_fields  every required key is present (and non-null)
  - risk_flags_present      expected flags appear in a flags list (recall)
  - risk_flags_absent       flags that must NOT appear (precision — catches
                             false-positive risk-aversion, see README)
"""
from __future__ import annotations

import os
import re


def _dig(obj, path: str):
    """'a.b.c' -> obj['a']['b']['c']. Raises KeyError/TypeError on a bad path
    so callers can turn that into a clear failed-check reason."""
    cur = obj
    for part in path.split("."):
        if isinstance(cur, list):
            cur = cur[int(part)]
        else:
            cur = cur[part]
    return cur


# ---------------------------------------------------------------------------
# Structured-JSON graders
# ---------------------------------------------------------------------------

def grade_json_field_equals(result, check, context=None):
    path, expected = check["path"], check["expected"]
    try:
        actual = _dig(result["output"], path)
    except (KeyError, TypeError, IndexError) as exc:
        return {"score": 0.0, "reason": f"Path '{path}' not found in output: {exc}"}
    if isinstance(actual, str) and isinstance(expected, str):
        match = actual.strip().lower() == expected.strip().lower()
    else:
        match = actual == expected
    if match:
        return {"score": 1.0, "reason": f"{path} = {actual!r} (expected {expected!r})"}
    return {"score": 0.0, "reason": f"{path} = {actual!r}, expected {expected!r}"}


def grade_json_field_tolerance(result, check, context=None):
    path = check["path"]
    expected = float(check["expected"])
    tolerance_pct = check.get("tolerance_pct")
    tolerance_abs = check.get("tolerance_abs", 0.01 if tolerance_pct is None else None)
    try:
        actual = _dig(result["output"], path)
    except (KeyError, TypeError, IndexError) as exc:
        return {"score": 0.0, "reason": f"Path '{path}' not found in output: {exc}"}
    try:
        actual = float(actual)
    except (TypeError, ValueError):
        return {"score": 0.0, "reason": f"{path} = {actual!r} is not numeric"}

    if tolerance_pct is not None:
        allowed = abs(expected) * (tolerance_pct / 100.0)
    else:
        allowed = tolerance_abs
    diff = abs(actual - expected)
    if diff <= allowed:
        return {"score": 1.0, "reason": f"{path} = {actual} (expected {expected} +/- {allowed:.4g})"}
    return {"score": 0.0, "reason": f"{path} = {actual}, expected {expected} +/- {allowed:.4g} (diff {diff:.4g})"}


def grade_list_field_match(result, check, context=None):
    """check = {"path": "...", "expected": [...], "mode": "exact"|"subset"|"superset"}
    "subset": every expected item must appear (recall; extra items OK).
    "superset": every actual item must be in expected (precision; missing OK).
    "exact": both directions must hold (default)."""
    path = check["path"]
    expected = set(check["expected"])
    mode = check.get("mode", "exact")
    try:
        actual_raw = _dig(result["output"], path)
    except (KeyError, TypeError, IndexError) as exc:
        return {"score": 0.0, "reason": f"Path '{path}' not found in output: {exc}"}
    if not isinstance(actual_raw, list):
        return {"score": 0.0, "reason": f"{path} is not a list: {actual_raw!r}"}
    key = check.get("key")
    actual = set((item.get(key) if isinstance(item, dict) else item) for item in actual_raw)

    missing = expected - actual
    extra = actual - expected
    if mode == "subset" and not missing:
        return {"score": 1.0, "reason": f"All {len(expected)} expected items present in {path}"}
    if mode == "superset" and not extra:
        return {"score": 1.0, "reason": f"No unexpected items in {path}"}
    if mode == "exact" and not missing and not extra:
        return {"score": 1.0, "reason": f"{path} matches expected set exactly ({len(expected)} items)"}
    return {"score": 0.0, "reason": f"{path} mismatch — missing={sorted(missing)[:10]}, extra={sorted(extra)[:10]}"}


def grade_schema_required_fields(result, check, context=None):
    required = check["required"]
    root_path = check.get("path")
    try:
        root = _dig(result["output"], root_path) if root_path else result["output"]
    except (KeyError, TypeError, IndexError) as exc:
        return {"score": 0.0, "reason": f"Root path '{root_path}' not found: {exc}"}
    if not isinstance(root, dict):
        return {"score": 0.0, "reason": f"Expected an object at '{root_path or '<root>'}', got {type(root).__name__}"}
    missing = [f for f in required if root.get(f) is None]
    if missing:
        return {"score": 0.0, "reason": f"Missing/null required fields: {missing}"}
    return {"score": 1.0, "reason": f"All {len(required)} required fields present"}


def grade_risk_flags_present(result, check, context=None):
    path = check.get("path", "risk_flags")
    expected = set(check["expected"])
    try:
        actual = set(_dig(result["output"], path))
    except (KeyError, TypeError, IndexError) as exc:
        return {"score": 0.0, "reason": f"Path '{path}' not found in output: {exc}"}
    missing = expected - actual
    if missing:
        return {"score": 0.0, "reason": f"Missing expected risk flags: {sorted(missing)}. Actual: {sorted(actual)}"}
    return {"score": 1.0, "reason": f"All expected risk flags present: {sorted(expected)}"}


def grade_risk_flags_absent(result, check, context=None):
    """Guards against over-cautious agents that flag risk everywhere. A
    'safe' scenario should NOT trip these flags — see README's note on
    grading false-positive risk-aversion, not just missed risk."""
    path = check.get("path", "risk_flags")
    forbidden = set(check["expected"])
    try:
        actual = set(_dig(result["output"], path))
    except (KeyError, TypeError, IndexError) as exc:
        return {"score": 0.0, "reason": f"Path '{path}' not found in output: {exc}"}
    present = forbidden & actual
    if present:
        return {"score": 0.0, "reason": f"Unexpected (false-positive) risk flags present: {sorted(present)}"}
    return {"score": 1.0, "reason": f"None of the forbidden flags {sorted(forbidden)} were raised"}


# ---------------------------------------------------------------------------
# Free-text graders (carried over from day2/01_evals, unchanged in spirit)
# ---------------------------------------------------------------------------

def grade_response_contains(result, check, context=None):
    text = result.get("final_text", "").lower()
    target = str(check).lower()
    if target in text:
        return {"score": 1.0, "reason": f"Found '{check}' in response"}
    return {"score": 0.0, "reason": f"'{check}' not found in response: {result.get('final_text', '')[:200]}"}


def grade_response_numeric(result, check, context=None):
    if isinstance(check, (int, float)):
        value, tolerance = float(check), 0.01
    else:
        value = float(check["value"])
        tolerance = float(check.get("tolerance", 0.01))
    text = result.get("final_text", "")
    numbers = re.findall(r"-?[\d,]+\.?\d*", text)
    for num_str in numbers:
        try:
            num = float(num_str.replace(",", ""))
            if abs(num - value) <= tolerance:
                return {"score": 1.0, "reason": f"Found {num} (expected {value} +/- {tolerance})"}
        except ValueError:
            continue
    return {"score": 0.0, "reason": f"Expected {value} (+/- {tolerance}), found: {numbers[:10]}"}


def grade_llm_judge(result, check, context=None):
    """check: a natural-language pass/fail criterion, judged by Claude."""
    import anthropic
    client = anthropic.Anthropic()
    model = os.environ.get("EVAL_JUDGE_MODEL", "claude-haiku-4-5-20251001")
    text = result.get("final_text", "")
    prompt = (
        "You are grading an AI agent's response against one criterion. "
        "Answer with exactly one word: PASS or FAIL.\n\n"
        f"Criterion: {check}\n\n"
        f"Agent response:\n{text}\n"
    )
    response = client.messages.create(
        model=model, max_tokens=5, messages=[{"role": "user", "content": prompt}]
    )
    verdict = response.content[0].text.strip().upper()
    if verdict.startswith("PASS"):
        return {"score": 1.0, "reason": f"Judge: PASS — {check}"}
    return {"score": 0.0, "reason": f"Judge: FAIL — {check}"}


GRADER_REGISTRY = {
    "json_field_equals": grade_json_field_equals,
    "json_field_tolerance": grade_json_field_tolerance,
    "list_field_match": grade_list_field_match,
    "schema_required_fields": grade_schema_required_fields,
    "risk_flags_present": grade_risk_flags_present,
    "risk_flags_absent": grade_risk_flags_absent,
    "response_contains": grade_response_contains,
    "response_numeric": grade_response_numeric,
    "llm_judge": grade_llm_judge,
}
