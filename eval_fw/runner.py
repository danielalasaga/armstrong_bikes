"""Eval harness: runs a task suite against an agent_fn, grades it, reports it.

Structurally this is the same runner/grader loop as
day2/01_evals/Building_an_Eval.ipynb (run_single_task -> run_eval ->
save_results/print_summary, GRADER_REGISTRY lookup, "a task passes only if
every check from every grader passes"). The difference is what a "result" is:
that notebook's agent is a chat tool-user, so its result carries a transcript
and tool_calls; these agents are data-in/data-out, so a result carries
`output` (parsed JSON) and `final_text` (raw text, for the narrative graders).
"""
from __future__ import annotations

import json
import os
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed

from graders import GRADER_REGISTRY


def run_single_task(agent_fn, task: dict, model=None) -> dict:
    start = time.time()
    try:
        raw = agent_fn(task["input"], task["output_type"], eval_mode=True, model=model)
    except Exception:
        return {
            "task_id": task["id"], "task_description": task.get("description", ""),
            "input": task["input"], "category": task.get("category", ""),
            "error": traceback.format_exc(), "passed": False, "grades": [],
            "metrics": {"time": round(time.time() - start, 3)},
        }

    elapsed = time.time() - start
    result = {"output": raw.get("output", {}), "final_text": raw.get("final_text", "")}
    usage = raw.get("usage", {})
    metrics = {
        "time": round(elapsed, 3),
        "input_tokens": usage.get("input_tokens", 0),
        "output_tokens": usage.get("output_tokens", 0),
    }

    grades = []
    context = {"input": task["input"], "task_id": task["id"], "model": model}
    for grader in task.get("graders", []):
        grader_fn = GRADER_REGISTRY.get(grader["type"])
        if grader_fn is None:
            grades.append({"type": grader["type"], "check": None, "score": 0.0,
                            "reason": f"Unknown grader: {grader['type']}"})
            continue
        for check in grader.get("checks", []):
            try:
                grade = grader_fn(result, check, context)
                grades.append({"type": grader["type"], "check": check, "score": grade["score"],
                                "reason": grade["reason"]})
            except Exception as exc:
                grades.append({"type": grader["type"], "check": check, "score": 0.0,
                                "reason": f"grader error: {type(exc).__name__}: {exc}"})

    passed = all(g["score"] == 1.0 for g in grades) if grades else False

    return {
        "task_id": task["id"], "task_description": task.get("description", ""),
        "input": task["input"], "category": task.get("category", ""),
        "passed": passed, "grades": grades, "metrics": metrics,
        "output": result["output"], "final_text": result["final_text"],
    }


def run_eval(agent_fn, tasks: list[dict], model=None, num_runs: int = 1, max_workers: int = 5) -> dict:
    """Run the full eval suite. Returns structured results (same shape as
    day2/01_evals' eval_results/*.json: {"runs": [...], "config": {...}})."""
    all_runs = []
    for _ in range(num_runs):
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(run_single_task, agent_fn, t, model): t for t in tasks}
            run_results = []
            for f in as_completed(futures):
                r = f.result()
                run_results.append(r)
                mark = "PASS" if r["passed"] else ("ERROR" if r.get("error") else "FAIL")
                print(f"  [{len(run_results)}/{len(tasks)}] {r['task_id']}: {mark}", flush=True)
        task_order = {t["id"]: i for i, t in enumerate(tasks)}
        run_results.sort(key=lambda r: task_order.get(r["task_id"], 999))
        all_runs.append(run_results)
    return {"runs": all_runs, "config": {"model": model, "num_runs": num_runs, "num_tasks": len(tasks)}}


def save_results(results: dict, directory: str = "eval_results", label: str = "default") -> str:
    os.makedirs(directory, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"{directory}/eval_{label}_{timestamp}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"Results saved to {filename}")
    return filename


def print_summary(results: dict) -> None:
    config = results["config"]
    print(f"{'=' * 60}")
    print(f"EVAL RESULTS: {config['num_tasks']} tasks, {config['num_runs']} run(s)")
    if config.get("model"):
        print(f"Model: {config['model']}")
    print(f"{'=' * 60}\n")

    for run_idx, run in enumerate(results["runs"]):
        if config["num_runs"] > 1:
            print(f"--- Run {run_idx + 1} ---")
        passed = sum(1 for r in run if r["passed"])
        total = len(run)
        print(f"Overall: {passed}/{total} passed ({passed / total * 100:.0f}%)\n")

        categories = {}
        for r in run:
            cat = r.get("category", "uncategorized")
            categories.setdefault(cat, {"passed": 0, "total": 0})
            categories[cat]["total"] += 1
            if r["passed"]:
                categories[cat]["passed"] += 1
        if len(categories) > 1:
            print("By category:")
            for cat, c in sorted(categories.items()):
                print(f"  {cat}: {c['passed']}/{c['total']} ({c['passed'] / c['total'] * 100:.0f}%)")
            print()

        print("Tasks:")
        for r in run:
            mark = "PASS" if r["passed"] else "FAIL"
            print(f"  [{mark}] {r['task_id']}: {r['task_description']}")
            if not r["passed"]:
                for g in r.get("grades", []):
                    if g["score"] != 1.0:
                        print(f"    - {g['type']}: {g['reason'][:160]}")
                if r.get("error"):
                    print(f"    Error: {r['error'][:200]}")

        ok = [r for r in run if not r.get("error")]
        if ok:
            print(f"\nMetrics (avg): {sum(r['metrics']['time'] for r in ok) / len(ok):.2f}s")
            print(f"Tokens: {sum(r['metrics']['input_tokens'] for r in ok):,} in, "
                  f"{sum(r['metrics']['output_tokens'] for r in ok):,} out")
        print()
