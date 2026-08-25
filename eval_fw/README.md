# Bike Sourcing Eval Framework

Evals for the three agent outputs described in `BIKE_SOURCING_SUMMARY.md`'s
architecture: **Parts List**, **Sourcing / Cost & Lead-Time**, and **Supply
Risk** — plus an integration suite for the coordinator's final memo.

Structurally this follows the pattern in `day2/01_evals/Building_an_Eval.ipynb`:
a task is `{id, description, graders: [{type, checks}]}`, a runner executes
each task against an `agent_fn` and applies every grader, and a task passes
only if every check from every grader scores 1.0. Results are saved to
`eval_results/*.json` in the same shape that notebook produces.

## Why the eval logic differs from the original plan

The plan was drafted against the *skill files* (`cost-optimizer.md`,
`lead-time-critical-path.md`, etc.), which describe a multi-supplier-quote
world: incoterms (FOB/CIF/DDP), currency conversion, MOQ surcharges, duty
brackets. The actual `Hackathon Data/` is simpler and different in kind:

- **Exactly one supplier per part** (`parts_catalog.json`) — there is no
  "cheapest of N quotes" decision to grade. Cost-optimization-across-quotes
  tasks were dropped entirely.
- **Costs already normalized to USD** — no currency/incoterm/duty math to check.
- **No `supply-risk.md` skill file at all.** The original hackathon pack
  described one (`FINAL_DELIVERABLES.txt` references it under "reference
  data from original pack"), but it isn't in this repo. `agents.py`'s
  `claude_agent` writes its own system prompt for the risk specialist rather
  than loading a skill file that doesn't exist — treat that prompt as a
  first draft of the missing `supply-risk.md`, not a finished spec.
- **What the real data supports well instead:** parts-list fidelity against
  `bill_of_materials.json`, cost/lead-time roll-ups against
  `assembly_estimates.json`, and supply-risk signals computed from
  `suppliers.json` (reliability, capacity, geography) joined against the BOM.
  Those are the three suites here.

## Known data quality issue

`bill_of_materials.json`'s per-line `unit_cost_usd * qty` always matches its
own `line_cost_usd` — but the file's top-level `total_parts_cost_usd` header
does **not** match `sum(line_cost_usd)` for **any** of the 6 SKUs (off by
$11–$172, no consistent direction). `golden.py` trusts the recomputed sum
(individual lines check out) and exposes both:
`total_parts_cost_usd` (trusted) vs. `header_total_parts_cost_usd` (file's
claim) vs. `header_total_matches_sum` (always `False` today). If you fix the
source file, `header_total_matches_sum` becomes a good regression check —
until then, don't grade an agent against the header field.

## Folder structure

```
data_loader.py    Loads + cross-indexes the 6 Hackathon Data JSON files (cached)
golden.py         Ground truth, computed from the data — not hand-typed
scenarios.py      Per-SKU volume tiers & deadlines, sized off real supplier capacity
graders.py        GRADER_REGISTRY — structured-JSON graders + the day2 free-text ones
tasks.py          Builds the 4 task suites from golden.py + scenarios.py
agents.py         agent_fn implementations: `reference` (deterministic) and `claude` (real API)
runner.py         run_eval / save_results / print_summary (adapted from day2's runner)
run_evals.py      CLI entry point
eval_results/     Output JSON, one file per run
```

## How to run

```bash
cd eval_fw
pip install -r requirements.txt        # only needed for --agent claude / llm_judge checks

# 1. Self-check the harness first — should be ~100% (any FAIL here is a bug
#    in golden.py/tasks.py/graders.py, not in an agent):
python run_evals.py --agent reference --suite all

# 2. Point it at the real coordinator once you're wiring one up:
export ANTHROPIC_API_KEY=sk-ant-...
python run_evals.py --agent claude --suite parts_list
python run_evals.py --agent claude --suite all --num-runs 3   # check run-to-run consistency
```

`--agent reference` currently passes 48/48. Treat that as the harness sanity
check, not a claim about a real agent's accuracy — it's computed straight
from `golden.py` by construction.

## The 4 task suites (48 tasks total)

| Suite | Tasks | What it checks |
|---|---|---|
| `parts_list` | 6 (1/SKU) | Exact part-number set match, total cost, critical-path part |
| `cost_leadtime` | 18 (3/SKU) | `comfortable_on_time`, `late_deadline` (must flag late), `overcommit_infeasible` (must flag capacity-infeasible) |
| `supply_risk` | 18 (3/SKU) | `safe_volume` (only `single_source_bom` should fire), `stress_volume` (concentration should fire, infeasible should NOT), `overcommit_volume` (infeasible should fire) |
| `memo` | 6 (1/SKU) | Integration: coordinator output on the "classic conflict" shape (cost's fine, schedule/capacity is tight) — schema, numbers, risk flags, and an `llm_judge` check that the memo explains *why*, not just *what* |

`cost_leadtime` and `supply_risk` scenarios are sized per-SKU from the
**effective** tightest supplier capacity — the capacity of the supplier that
provides the *most* parts on that bike, divided by how many parts they
provide (e.g. SteelPath supplies all 7 drivetrain parts on the MTB, so its
true per-bike constraint is `80,000 / 7 ≈ 11,428` units, not the raw 80,000).
Sizing tiers off raw per-supplier capacity instead of this effective number
was an actual bug caught while building this suite — `stress_volume` was
tripping `supplier_capacity_infeasible` for multi-part suppliers well before
the intended `overcommit_volume` tier. Fixed in `scenarios.py::_tightest_supplier_capacity`.

## Grader notes

- `risk_flags_absent` is deliberately paired with `risk_flags_present` on the
  `safe_volume` and `stress_volume` scenarios — this catches an
  over-cautious agent that flags risk everywhere just as much as one that
  misses real risk. Don't delete the "absent" checks when a suite starts
  passing; they're the ones proving the agent isn't just flagging
  everything as risky.
- `json_field_tolerance` defaults to `tolerance_pct` when given, else an
  absolute `tolerance_abs` (default $0.01) — use `tolerance_pct` for
  program-scale totals and `tolerance_abs`/default for per-unit costs.
- `llm_judge` calls Claude (`EVAL_JUDGE_MODEL`, default
  `claude-haiku-4-5-20251001`) and needs `ANTHROPIC_API_KEY` — it's the only
  grader that costs money/latency, so it's used sparingly (2 checks, only in
  the `memo` suite).

## Risk thresholds (`golden.py`)

Chosen to be defensible, not fit to any one scenario — revisit them with
whoever owns real sourcing risk tolerance before trusting them in production:

- `CAPACITY_CONCENTRATION_WARN_PCT = 50` — order consumes >50% of a
  supplier's annual capacity (leaves no room for a second customer or a
  reorder)
- `CAPACITY_INFEASIBLE_PCT = 100` — order exceeds capacity outright
- `LOW_RELIABILITY_THRESHOLD = 4.5` — below this on `suppliers.json`'s 0–5
  `reliability_score`
- `GEOGRAPHIC_CONCENTRATION_WARN_PCT = 50` — >50% of BOM line-cost value
  from one country
- `THIN_SCHEDULE_BUFFER_PCT = 10` — assembly+QC buffer under 10% of the
  critical-path lead time

## Extending this

- **Wire the real coordinator**: `agents.py::claude_agent` calls each
  specialist independently per `output_type`. If/when there's an actual
  coordinator agent (loading all 3+ skills and doing the conflict-resolution
  handoff itself), add it to `AGENT_REGISTRY` as e.g. `coordinator_agent` —
  the task/grader layer doesn't need to change, since it grades the output
  shape, not how it was produced.
- **Write `supply-risk.md`**: `agents.py::_SUPPLY_RISK_SYSTEM_PROMPT` is a
  working first draft of the missing skill. Promoting it to a real skill
  file (and pointing `claude_agent` at it the same way the other three
  output types load theirs) would close that gap.
- **New scenarios**: add entries to `scenarios.py`'s tier/deadline builders
  — everything downstream (`tasks.py`, goldens) regenerates from real data
  automatically, nothing to hand-edit.
