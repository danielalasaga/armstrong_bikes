"""Pluggable agents-under-test.

Every agent function has the signature:
    agent_fn(task_input: dict, output_type: str, eval_mode=True, model=None) -> dict

...and returns {"output": <parsed JSON dict>, "final_text": <raw text>,
"usage": {"input_tokens": int, "output_tokens": int}}. The runner (runner.py)
wraps this with timing/error handling and hands `output`/`final_text` to the
graders in graders.py.

Two agents are provided:

  reference_agent  Deterministic, computed straight from golden.py. Scores
                    ~100% by construction — its job is to prove the harness
                    itself (data loading, scenario generation, grading) is
                    wired correctly BEFORE you point it at a real model. Run
                    this first after any change to golden.py/tasks.py/graders.py.

  claude_agent      Calls the actual Anthropic API, assembling a system prompt
                    from the repo's skill files (bom-structure.md,
                    cost-optimizer.md, lead-time-critical-path.md,
                    sourcing-recommendation.md) plus the real per-SKU data
                    slice, and asks for strict JSON matching the schema the
                    graders check. This is the one you iterate against.

IMPORTANT — a known mismatch you should expect the first claude_agent run to
surface: the skill files describe a multi-supplier-quote, incoterm/currency
costing model (see cost-optimizer.md), but the actual Hackathon Data has
exactly one supplier per part with costs already in USD, and NO skill file
for supply-risk at all (the original hackathon pack's supply-risk.md never
made it into this repo — see FINAL_DELIVERABLES.txt). claude_agent works
around this by not relying on the skill files where they don't apply: it
builds the supply_risk system prompt itself, and it grounds cost_leadtime
context in the real data rather than the skill's incoterm framing. Expect the
first eval run to be a signal that those skill files need rewriting to match
the actual dataset, not a signal that the eval suite is wrong — that mismatch
is precisely the kind of thing this suite exists to catch.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

from data_loader import load_all
from golden import parts_list_golden, cost_leadtime_golden, supply_risk_golden

REPO_ROOT = Path(__file__).resolve().parent.parent
MODEL = os.environ.get("EVAL_MODEL", "claude-sonnet-5")


# ---------------------------------------------------------------------------
# Reference agent — deterministic, for harness self-checks
# ---------------------------------------------------------------------------

def reference_agent(task_input: dict, output_type: str, eval_mode: bool = True, model=None) -> dict:
    if output_type == "parts_list":
        golden = parts_list_golden(task_input["bike_sku"])
        output = {
            "bike_sku": golden["bike_sku"],
            "bike_model": golden["bike_model"],
            "parts": golden["parts"],
            "total_parts_cost_usd": golden["total_parts_cost_usd"],
            "critical_path_part": golden["critical_path_part"],
            "critical_path_lead_days": golden["critical_path_lead_days"],
        }
        text = f"Parts list for {golden['bike_model']}: {golden['total_part_lines']} lines, " \
               f"${golden['total_parts_cost_usd']:.2f} total."

    elif output_type == "cost_leadtime":
        golden = cost_leadtime_golden(
            task_input["bike_sku"], task_input["volume"], task_input.get("assembly_deadline_day")
        )
        output = golden
        text = (f"{golden['bike_model']}: ${golden['cost_per_bike_usd']:.2f}/bike, "
                f"${golden['total_program_cost_usd']:,.2f} total program cost. "
                f"Critical path: {golden['critical_path_part']} ({golden['critical_path_lead_days']}d). "
                f"{'On time' if golden['on_time'] else 'LATE'} against day {golden['assembly_deadline_day']}.")

    elif output_type == "supply_risk":
        golden = supply_risk_golden(task_input["bike_sku"], task_input["volume"])
        output = golden
        text = f"{golden['bike_model']} risk flags: {', '.join(golden['risk_flags'])}. " \
               f"Top sourcing country: {golden['top_country']} ({golden['top_country_pct']}% of BOM cost)."

    elif output_type == "memo":
        cost = cost_leadtime_golden(
            task_input["bike_sku"], task_input["volume"], task_input.get("assembly_deadline_day")
        )
        risk = supply_risk_golden(task_input["bike_sku"], task_input["volume"])
        summary = (
            f"Recommend proceeding with the current single-source plan for {cost['bike_model']} "
            f"at {task_input['volume']:,} units. Program cost ${cost['total_program_cost_usd']:,.0f} "
            f"(${cost['cost_per_bike_usd']:.2f}/bike). Critical path is {cost['critical_path_part']} "
            f"via {cost['critical_path_supplier_name']} at {cost['critical_path_lead_days']} days, "
            f"{'landing on schedule' if cost['on_time'] else 'missing the deadline'} "
            f"(day {cost['assembly_deadline_day']}). Because the entire BOM is single-sourced, "
            f"we are carrying {', '.join(risk['risk_flags'])} as open risks that need a mitigation "
            f"decision before this is ready for approval."
        )
        output = {
            "bike_model": cost["bike_model"],
            "bike_sku": cost["bike_sku"],
            "total_program_cost_usd": cost["total_program_cost_usd"],
            "critical_path_part": cost["critical_path_part"],
            "on_time": cost["on_time"],
            "risk_flags": risk["risk_flags"],
            "executive_summary": summary,
        }
        text = summary

    else:
        raise ValueError(f"Unknown output_type: {output_type!r}")

    usage_estimate = max(50, len(text) // 4)
    return {"output": output, "final_text": text,
            "usage": {"input_tokens": 0, "output_tokens": usage_estimate}}


# ---------------------------------------------------------------------------
# Claude agent — real model call per specialist
# ---------------------------------------------------------------------------

_SKILL_FILES = {
    "parts_list": "bom-structure.md",
    "cost_leadtime": ["cost-optimizer.md", "lead-time-critical-path.md"],
    "memo": "sourcing-recommendation.md",
}


def _read_skill(filename: str) -> str:
    path = REPO_ROOT / filename
    return path.read_text(encoding="utf-8") if path.exists() else f"[skill file {filename} not found]"


def _data_context_for_sku(sku: str) -> dict:
    """A compact per-SKU slice of the real data — not the whole catalog —
    so the prompt stays small and the agent can't 'cheat' by peeking at
    other bikes' answers."""
    data = load_all()
    bom = data["bom_by_sku"][sku]
    assembly = data["assembly_by_sku"][sku]
    model = data["models_by_sku"][sku]
    supplier_ids = {data["parts_by_number"][line["part_number"]]["supplier_id"] for line in bom["bom"]}
    suppliers = {sid: data["suppliers_by_id"][sid] for sid in supplier_ids}
    parts_catalog_slice = {
        line["part_number"]: data["parts_by_number"][line["part_number"]] for line in bom["bom"]
    }
    return {
        "bike_model": model,
        "bill_of_materials": bom,
        "assembly_estimate": assembly,
        "parts_catalog_slice": parts_catalog_slice,
        "suppliers": suppliers,
    }


_SUPPLY_RISK_SYSTEM_PROMPT = """You are the Supply Risk specialist in a bike-sourcing multi-agent \
system. Given one bike model's bill of materials, its parts catalog entries, and its suppliers, \
assess sourcing risk for a specific order volume.

Score these signals explicitly:
- Single-source exposure: is each part sourced from exactly one supplier with no listed alternative?
- Geographic concentration: what % of BOM line-cost value comes from each supplier country? Flag \
  if any one country exceeds 50%.
- Supplier capacity: for each supplier used, compare (order volume * qty_per_bike demanded from \
  them) against their annual_capacity_units. Flag "supplier_capacity_concentration" at >=50% \
  utilization, and "supplier_capacity_infeasible" if utilization exceeds 100%.
- Supplier reliability: flag any supplier used with reliability_score < 4.5.
- Schedule buffer: compare the assembly_and_qc_days buffer against the critical-path lead time; \
  flag "thin_schedule_buffer" if that buffer is under 10% of the critical-path lead days.
- Always include "single_source_bom" in risk_flags — every part in this dataset has exactly one \
  supplier, so this is a structural fact, not a maybe.

Respond with ONLY a JSON object (no markdown fences, no commentary) with this shape:
{
  "bike_sku": str, "bike_model": str, "volume": int,
  "risk_flags": [str, ...],
  "top_country": str, "top_country_pct": number,
  "critical_path_supplier_reliability": number,
  "capacity_risk_suppliers": [{"supplier_id": str, "utilization_pct": number, "infeasible": bool}]
}"""

_OUTPUT_SCHEMAS = {
    "parts_list": (
        '{"bike_sku": str, "bike_model": str, "parts": [{"part_number": str, "qty": int, '
        '"unit_cost_usd": number, "line_cost_usd": number, "supplier_id": str}], '
        '"total_parts_cost_usd": number, "critical_path_part": str, "critical_path_lead_days": int}'
    ),
    "cost_leadtime": (
        '{"bike_sku": str, "volume": int, "cost_per_bike_usd": number, "total_program_cost_usd": number, '
        '"critical_path_part": str, "critical_path_lead_days": int, "total_d2c_fulfillment_days_max": int, '
        '"assembly_deadline_day": int|null, "on_time": bool, "days_margin": int|null, '
        '"critical_path_supplier_capacity_utilization_pct": number, "capacity_infeasible": bool}'
    ),
    "memo": (
        '{"bike_model": str, "bike_sku": str, "total_program_cost_usd": number, "critical_path_part": str, '
        '"on_time": bool, "risk_flags": [str], "executive_summary": str}'
    ),
}


def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n|```$", "", text.strip(), flags=re.MULTILINE).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise


def claude_agent(task_input: dict, output_type: str, eval_mode: bool = True, model=None) -> dict:
    import anthropic
    client = anthropic.Anthropic()
    sku = task_input["bike_sku"]
    context = _data_context_for_sku(sku)

    if output_type == "supply_risk":
        system_prompt = _SUPPLY_RISK_SYSTEM_PROMPT
    else:
        skill_names = _SKILL_FILES[output_type]
        skill_names = skill_names if isinstance(skill_names, list) else [skill_names]
        skills_text = "\n\n---\n\n".join(_read_skill(name) for name in skill_names)
        system_prompt = (
            f"You are a specialist in a bike-sourcing multi-agent system. Reference material "
            f"(Skill files) follows — apply the reasoning it describes, but ground every number in "
            f"the ACTUAL data provided in the user message, not in any example numbers from the "
            f"Skill files themselves.\n\n{skills_text}\n\n"
            f"Respond with ONLY a JSON object (no markdown fences, no commentary) matching this shape: "
            f"{_OUTPUT_SCHEMAS[output_type]}"
        )

    user_message = json.dumps({"request": task_input, "data": context}, default=str)
    response = client.messages.create(
        model=model or MODEL,
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    text = response.content[0].text
    output = _extract_json(text)
    return {
        "output": output,
        "final_text": text,
        "usage": {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        },
    }


AGENT_REGISTRY = {
    "reference": reference_agent,
    "claude": claude_agent,
}
