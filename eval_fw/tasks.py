"""Builds the task suites the runner executes.

Each task is:
    {"id", "description", "category", "output_type", "input", "graders": [...]}

`output_type` tells agents.py which specialist to invoke (parts_list,
cost_leadtime, supply_risk, or memo for the integration/coordinator suite).
`input` is the structured payload passed to that agent — not a chat string,
since these are data-in/data-out agents (see golden.py's module docstring for
why this suite dropped the chat-style cost-optimizer grading originally
planned from the skill docs).

Every expected value below comes from golden.py, computed from the live
Hackathon Data — nothing here is hand-typed, so the suite regenerates
correctly if the dataset changes.
"""
from __future__ import annotations

from golden import parts_list_golden, cost_leadtime_golden, supply_risk_golden
from scenarios import all_skus, volume_tiers, deadline_scenarios, critical_path_overcommit_volume


def build_parts_list_tasks() -> list[dict]:
    tasks = []
    for sku in all_skus():
        golden = parts_list_golden(sku)
        tasks.append({
            "id": f"parts_list__{sku}",
            "description": f"Parts list for {golden['bike_model']} ({sku})",
            "category": "parts_list",
            "output_type": "parts_list",
            "input": {"bike_sku": sku},
            "graders": [
                {"type": "schema_required_fields", "checks": [
                    {"required": ["bike_sku", "parts", "total_parts_cost_usd",
                                   "critical_path_part", "critical_path_lead_days"]},
                ]},
                {"type": "list_field_match", "checks": [
                    {"path": "parts", "key": "part_number",
                     "expected": golden["part_numbers"], "mode": "exact"},
                ]},
                {"type": "json_field_tolerance", "checks": [
                    {"path": "total_parts_cost_usd", "expected": golden["total_parts_cost_usd"],
                     "tolerance_pct": 0.5},
                ]},
                {"type": "json_field_equals", "checks": [
                    {"path": "critical_path_part", "expected": golden["critical_path_part"]},
                    {"path": "bike_sku", "expected": sku},
                ]},
            ],
        })
    return tasks


def build_cost_leadtime_tasks() -> list[dict]:
    tasks = []
    for sku in all_skus():
        volumes = volume_tiers(sku)
        deadlines = deadline_scenarios(sku, volumes["safe"])
        # Sized to the critical-path supplier's own capacity specifically —
        # NOT volumes["overcommit"], which targets the aggregate cross-
        # supplier bottleneck (often a different supplier). See
        # scenarios.critical_path_overcommit_volume for why the two must
        # not be conflated.
        cp_overcommit_volume = critical_path_overcommit_volume(sku)

        scenario_defs = [
            ("comfortable_on_time", volumes["safe"], deadlines["comfortable"], True, False),
            ("late_deadline", volumes["safe"], deadlines["late"], False, False),
            ("overcommit_infeasible", cp_overcommit_volume, deadlines["comfortable"], None, True),
        ]
        for label, volume, deadline, expect_on_time, expect_infeasible in scenario_defs:
            golden = cost_leadtime_golden(sku, volume=volume, assembly_deadline_day=deadline)
            checks = [
                {"path": "cost_per_bike_usd", "expected": golden["cost_per_bike_usd"], "tolerance_pct": 0.5},
                {"path": "total_program_cost_usd", "expected": golden["total_program_cost_usd"], "tolerance_pct": 0.5},
            ]
            equals_checks = [
                {"path": "critical_path_part", "expected": golden["critical_path_part"]},
            ]
            if expect_on_time is not None:
                equals_checks.append({"path": "on_time", "expected": expect_on_time})
            equals_checks.append({"path": "capacity_infeasible", "expected": expect_infeasible})

            tasks.append({
                "id": f"cost_leadtime__{sku}__{label}",
                "description": f"Cost/lead-time for {golden['bike_model']} — {label} "
                                f"(vol={volume}, deadline=day {deadline})",
                "category": "cost_leadtime",
                "output_type": "cost_leadtime",
                "input": {"bike_sku": sku, "volume": volume, "assembly_deadline_day": deadline},
                "graders": [
                    {"type": "schema_required_fields", "checks": [
                        {"required": ["cost_per_bike_usd", "total_program_cost_usd", "critical_path_part",
                                       "on_time", "capacity_infeasible"]},
                    ]},
                    {"type": "json_field_tolerance", "checks": checks},
                    {"type": "json_field_equals", "checks": equals_checks},
                ],
            })
    return tasks


def build_supply_risk_tasks() -> list[dict]:
    tasks = []
    for sku in all_skus():
        volumes = volume_tiers(sku)

        for label, volume, expect_present, expect_absent in [
            ("safe_volume", volumes["safe"],
             ["single_source_bom"],
             ["supplier_capacity_concentration", "supplier_capacity_infeasible"]),
            ("stress_volume", volumes["stress"],
             ["single_source_bom", "supplier_capacity_concentration"],
             ["supplier_capacity_infeasible"]),
            ("overcommit_volume", volumes["overcommit"],
             ["single_source_bom", "supplier_capacity_concentration", "supplier_capacity_infeasible"],
             []),
        ]:
            golden = supply_risk_golden(sku, volume=volume)
            tasks.append({
                "id": f"supply_risk__{sku}__{label}",
                "description": f"Supply risk for {golden['bike_model']} — {label} (vol={volume})",
                "category": "supply_risk",
                "output_type": "supply_risk",
                "input": {"bike_sku": sku, "volume": volume},
                "graders": [
                    {"type": "schema_required_fields", "checks": [
                        {"required": ["risk_flags", "top_country", "critical_path_supplier_reliability"]},
                    ]},
                    {"type": "risk_flags_present", "checks": [{"expected": expect_present}]},
                    {"type": "risk_flags_absent", "checks": [{"expected": expect_absent}]} if expect_absent else None,
                    {"type": "json_field_equals", "checks": [
                        {"path": "top_country", "expected": golden["top_country"]},
                    ]},
                ],
            })
            tasks[-1]["graders"] = [g for g in tasks[-1]["graders"] if g is not None]
    return tasks


def build_memo_tasks() -> list[dict]:
    """Integration suite: exercises the coordinator end-to-end on the
    'classic conflict' shape — a volume that's fine on cost but tight on
    schedule/capacity, which is exactly the case the coordinator exists to
    resolve (see BIKE_SOURCING_SUMMARY.md's Shanghai/Taiwan frame example)."""
    tasks = []
    for sku in all_skus():
        volumes = volume_tiers(sku)
        deadlines = deadline_scenarios(sku, volumes["stress"])
        volume, deadline = volumes["stress"], deadlines["boundary"]
        cost_golden = cost_leadtime_golden(sku, volume=volume, assembly_deadline_day=deadline)
        risk_golden = supply_risk_golden(sku, volume=volume)

        tasks.append({
            "id": f"memo__{sku}",
            "description": f"Full sourcing memo for {cost_golden['bike_model']} "
                            f"(vol={volume}, deadline=day {deadline})",
            "category": "memo",
            "output_type": "memo",
            "input": {"bike_sku": sku, "volume": volume, "assembly_deadline_day": deadline},
            "graders": [
                {"type": "schema_required_fields", "checks": [
                    {"required": ["bike_model", "total_program_cost_usd", "critical_path_part",
                                   "on_time", "risk_flags", "executive_summary"]},
                ]},
                {"type": "json_field_tolerance", "checks": [
                    {"path": "total_program_cost_usd", "expected": cost_golden["total_program_cost_usd"],
                     "tolerance_pct": 1.0},
                ]},
                {"type": "risk_flags_present", "checks": [{"expected": risk_golden["risk_flags"]}]},
                {"type": "llm_judge", "checks": [
                    "The response explains WHY the recommended supplier/plan was chosen, "
                    "not just WHAT was chosen (i.e. it gives a rationale, not just a table).",
                    "The executive summary is decision-oriented and under roughly 150 words.",
                ]},
            ],
        })
    return tasks


SUITE_BUILDERS = {
    "parts_list": build_parts_list_tasks,
    "cost_leadtime": build_cost_leadtime_tasks,
    "supply_risk": build_supply_risk_tasks,
    "memo": build_memo_tasks,
}


def build_all_tasks(suites: list[str] | None = None) -> list[dict]:
    suites = suites or list(SUITE_BUILDERS.keys())
    tasks = []
    for suite in suites:
        tasks.extend(SUITE_BUILDERS[suite]())
    return tasks


if __name__ == "__main__":
    for name, builder in SUITE_BUILDERS.items():
        t = builder()
        print(f"{name}: {len(t)} tasks")
