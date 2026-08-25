"""CLI entry point.

Examples:
    python run_evals.py                                  # reference agent, all suites
    python run_evals.py --agent reference --suite parts_list
    python run_evals.py --agent claude --suite supply_risk --model claude-sonnet-5
    python run_evals.py --agent claude --num-runs 3       # check consistency across runs
"""
from __future__ import annotations

import argparse

from agents import AGENT_REGISTRY
from tasks import SUITE_BUILDERS, build_all_tasks
from runner import run_eval, save_results, print_summary


def main():
    parser = argparse.ArgumentParser(description="Run the bike-sourcing eval suite.")
    parser.add_argument("--agent", choices=list(AGENT_REGISTRY.keys()), default="reference",
                         help="Which agent to evaluate (default: reference — the deterministic "
                              "harness self-check; use 'claude' to test the real model).")
    parser.add_argument("--suite", choices=list(SUITE_BUILDERS.keys()) + ["all"], default="all",
                         help="Which task suite to run (default: all).")
    parser.add_argument("--model", default=None, help="Override the model for the claude agent.")
    parser.add_argument("--num-runs", type=int, default=1, help="Repeat each task N times.")
    parser.add_argument("--max-workers", type=int, default=5)
    parser.add_argument("--no-save", action="store_true", help="Don't write eval_results/*.json.")
    args = parser.parse_args()

    suites = None if args.suite == "all" else [args.suite]
    tasks = build_all_tasks(suites)
    agent_fn = AGENT_REGISTRY[args.agent]

    print(f"Running {len(tasks)} tasks against agent='{args.agent}' "
          f"(suite={args.suite}, num_runs={args.num_runs})\n")
    results = run_eval(agent_fn, tasks, model=args.model, num_runs=args.num_runs, max_workers=args.max_workers)

    print()
    print_summary(results)
    if not args.no_save:
        save_results(results, label=f"{args.agent}_{args.suite}")


if __name__ == "__main__":
    main()
