"""Computes golden (ground-truth) expected outputs directly from Hackathon Data.

This is the source of truth the graders check agent outputs against. Every
number here is *derived*, not hand-typed — recomputing it from the raw JSON
files means the golden values stay correct if the dataset changes, and a
`--selfcheck` run (see run_evals.py) can catch internal inconsistencies in the
data itself (e.g. a line_cost_usd that doesn't equal unit_cost_usd * qty).

Design note on why this dataset changed the eval logic (see day2/01_evals
reference framework and the earlier architecture-doc-based plan):
  - The skill files (cost-optimizer.md etc.) describe a multi-supplier-quote,
    incoterm/currency/MOQ costing model. The actual Hackathon Data has exactly
    ONE supplier per part, costs already normalized to USD, and no incoterm/
    currency/duty fields at all. So there is no "cheapest of N quotes" choice
    to grade — cost-optimization tasks are gone from this eval suite.
  - What the real data DOES support well: parts-list fidelity, cost/lead-time
    roll-ups, and supply-risk signals (single-source concentration, supplier
    reliability, capacity vs. order volume, geographic concentration). Those
    are the three output types this framework evaluates.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from data_loader import load_all, parse_day_range

# Thresholds for deterministic risk flagging. Chosen to be defensible, not
# tuned to any one scenario — see README.md "Risk thresholds" for rationale.
CAPACITY_CONCENTRATION_WARN_PCT = 50.0   # order consumes >50% of a supplier's annual capacity
CAPACITY_INFEASIBLE_PCT = 100.0          # order exceeds a supplier's annual capacity outright
LOW_RELIABILITY_THRESHOLD = 4.5          # suppliers.json reliability_score is on a 0-5 scale
GEOGRAPHIC_CONCENTRATION_WARN_PCT = 50.0  # % of BOM line-cost value from one country
THIN_SCHEDULE_BUFFER_PCT = 10.0          # assembly+QC buffer as % of critical-path lead time


def extract_supplier_id(text: str) -> str:
    m = re.search(r"\(SUP-\d+\)", text)
    if not m:
        raise ValueError(f"Could not find a supplier id in: {text!r}")
    return m.group(0).strip("()")


def _extract_part_number(text: str) -> str:
    m = re.search(r"\(([A-Z]{2}-[A-Z0-9-]+)\)", text)
    if not m:
        raise ValueError(f"Could not find a part number in: {text!r}")
    return m.group(1)


# ---------------------------------------------------------------------------
# 1. Parts List
# ---------------------------------------------------------------------------

def parts_list_golden(sku: str) -> dict:
    data = load_all()
    bom = data["bom_by_sku"][sku]
    parts = []
    for line in bom["bom"]:
        catalog_entry = data["parts_by_number"].get(line["part_number"])
        if catalog_entry is None:
            raise ValueError(f"BOM references unknown part_number {line['part_number']!r} for {sku}")
        expected_line_cost = round(line["unit_cost_usd"] * line["qty"], 2)
        line_cost_ok = abs(expected_line_cost - line["line_cost_usd"]) <= 0.01
        parts.append({
            "part_number": line["part_number"],
            "part_name": line["part_name"],
            "qty": line["qty"],
            "unit_cost_usd": line["unit_cost_usd"],
            "line_cost_usd": line["line_cost_usd"],
            "supplier_id": catalog_entry["supplier_id"],
            "lead_time_days": catalog_entry["lead_time_days"],
            "part_family": catalog_entry["part_family"],
            "sub_family": catalog_entry["sub_family"],
            "on_critical_path": line["part_number"] == bom["critical_path_part"],
            "line_cost_consistent": line_cost_ok,
        })
    # golden total = recomputed sum of line costs (each line's unit_cost*qty
    # checks out individually in this dataset). The file's own top-level
    # `total_parts_cost_usd` header does NOT always match that sum — see
    # `header_total_matches_sum` below and README.md "Known data quality
    # issue". We trust the line items, not the header, and expose both so
    # graders/tasks can decide what to test.
    computed_total = round(sum(p["line_cost_usd"] for p in parts), 2)
    header_total = bom["total_parts_cost_usd"]
    return {
        "bike_sku": sku,
        "bike_model": bom["bike_model"],
        "total_part_lines": bom["total_part_lines"],
        "parts": parts,
        "part_numbers": sorted(p["part_number"] for p in parts),
        "total_parts_cost_usd": computed_total,
        "header_total_parts_cost_usd": header_total,
        "header_total_matches_sum": abs(computed_total - header_total) <= 0.01,
        "critical_path_part": bom["critical_path_part"],
        "critical_path_lead_days": bom["critical_path_lead_days"],
    }


# ---------------------------------------------------------------------------
# 2. Sourcing / Cost & Lead-Time
# ---------------------------------------------------------------------------

def cost_leadtime_golden(sku: str, volume: int, assembly_deadline_day: int | None = None) -> dict:
    data = load_all()
    bom = data["bom_by_sku"][sku]
    assembly = data["assembly_by_sku"][sku]
    breakdown = assembly["total_lead_time_breakdown"]
    lead = assembly["supplier_lead_times"]

    # Use the recomputed (line-item-verified) total, not the file's header
    # total — they disagree for some SKUs. See parts_list_golden().
    parts_cost_per_bike = parts_list_golden(sku)["total_parts_cost_usd"]
    labor_cost_per_unit = assembly["time_summary"]["labor_cost_per_unit_usd"]
    cost_per_bike = round(parts_cost_per_bike + labor_cost_per_unit, 2)
    total_program_cost = round(cost_per_bike * volume, 2)

    total_days_min, total_days_max = parse_day_range(breakdown["total_d2c_fulfillment_days_domestic"])
    outbound_min, outbound_max = parse_day_range(breakdown["outbound_shipping_days_domestic"])

    critical_supplier_id = extract_supplier_id(lead["critical_path_supplier"])
    critical_supplier = data["suppliers_by_id"][critical_supplier_id]

    on_time = assembly_deadline_day is not None and assembly_deadline_day >= total_days_max
    days_margin = None if assembly_deadline_day is None else assembly_deadline_day - total_days_max

    return {
        "bike_sku": sku,
        "bike_model": bom["bike_model"],
        "volume": volume,
        "parts_cost_per_bike_usd": parts_cost_per_bike,
        "labor_cost_per_unit_usd": labor_cost_per_unit,
        "cost_per_bike_usd": cost_per_bike,
        "total_program_cost_usd": total_program_cost,
        "critical_path_part": bom["critical_path_part"],
        "critical_path_part_name": lead["critical_path_part"],
        "critical_path_supplier_id": critical_supplier_id,
        "critical_path_supplier_name": critical_supplier["name"],
        "critical_path_lead_days": bom["critical_path_lead_days"],
        "supplier_production_days": breakdown["supplier_production_days"],
        "inbound_transit_days": breakdown["inbound_transit_days"],
        "assembly_and_qc_days": breakdown["assembly_and_qc_days"],
        "outbound_shipping_days_min": outbound_min,
        "outbound_shipping_days_max": outbound_max,
        "total_d2c_fulfillment_days_min": total_days_min,
        "total_d2c_fulfillment_days_max": total_days_max,
        "assembly_deadline_day": assembly_deadline_day,
        "on_time": on_time,
        "days_margin": days_margin,
        "critical_path_supplier_annual_capacity_units": critical_supplier["annual_capacity_units"],
        "critical_path_supplier_capacity_utilization_pct":
            round(volume / critical_supplier["annual_capacity_units"] * 100, 1),
        "capacity_infeasible": volume > critical_supplier["annual_capacity_units"],
    }


# ---------------------------------------------------------------------------
# 3. Supply Risk
# ---------------------------------------------------------------------------

def supply_risk_golden(sku: str, volume: int) -> dict:
    data = load_all()
    parts_list = parts_list_golden(sku)
    assembly = data["assembly_by_sku"][sku]
    bom = data["bom_by_sku"][sku]

    # Every part in this dataset has exactly one supplier_id -> the whole BOM
    # is single-sourced by construction. That is itself the headline risk
    # finding a risk agent should surface, not an edge case to special-case.
    demand_by_supplier: dict[str, float] = {}
    cost_by_country: dict[str, float] = {}
    total_cost = 0.0
    suppliers_used = set()
    for p in parts_list["parts"]:
        supplier = data["suppliers_by_id"][p["supplier_id"]]
        suppliers_used.add(p["supplier_id"])
        demand_by_supplier.setdefault(p["supplier_id"], 0.0)
        demand_by_supplier[p["supplier_id"]] += volume * p["qty"]
        cost_by_country.setdefault(supplier["country"], 0.0)
        cost_by_country[supplier["country"]] += p["line_cost_usd"]
        total_cost += p["line_cost_usd"]

    capacity_risk_suppliers = []
    for sid, demand_units in demand_by_supplier.items():
        capacity = data["suppliers_by_id"][sid]["annual_capacity_units"]
        utilization_pct = round(demand_units / capacity * 100, 1)
        if utilization_pct >= CAPACITY_CONCENTRATION_WARN_PCT:
            capacity_risk_suppliers.append({
                "supplier_id": sid,
                "supplier_name": data["suppliers_by_id"][sid]["name"],
                "demand_units": demand_units,
                "annual_capacity_units": capacity,
                "utilization_pct": utilization_pct,
                "infeasible": utilization_pct > CAPACITY_INFEASIBLE_PCT,
            })

    geographic_concentration = {
        country: round(cost / total_cost * 100, 1) for country, cost in cost_by_country.items()
    }
    top_country = max(geographic_concentration, key=geographic_concentration.get)
    top_country_pct = geographic_concentration[top_country]

    reliability_by_supplier = {
        sid: data["suppliers_by_id"][sid]["reliability_score"] for sid in suppliers_used
    }
    low_reliability_suppliers = [
        {"supplier_id": sid, "reliability_score": score, "supplier_name": data["suppliers_by_id"][sid]["name"]}
        for sid, score in reliability_by_supplier.items() if score < LOW_RELIABILITY_THRESHOLD
    ]

    critical_supplier_id = extract_supplier_id(assembly["supplier_lead_times"]["critical_path_supplier"])
    critical_reliability = data["suppliers_by_id"][critical_supplier_id]["reliability_score"]

    critical_lead_days = bom["critical_path_lead_days"]
    buffer_days = assembly["total_lead_time_breakdown"]["assembly_and_qc_days"]
    buffer_pct = round(buffer_days / critical_lead_days * 100, 1)
    thin_schedule_buffer = buffer_pct < THIN_SCHEDULE_BUFFER_PCT

    risk_flags = []
    risk_flags.append("single_source_bom")  # always true in this dataset; see module docstring
    if top_country_pct >= GEOGRAPHIC_CONCENTRATION_WARN_PCT:
        risk_flags.append("geographic_concentration")
    if capacity_risk_suppliers:
        risk_flags.append("supplier_capacity_concentration")
    if any(s["infeasible"] for s in capacity_risk_suppliers):
        risk_flags.append("supplier_capacity_infeasible")
    if low_reliability_suppliers:
        risk_flags.append("low_reliability_supplier")
    if thin_schedule_buffer:
        risk_flags.append("thin_schedule_buffer")

    return {
        "bike_sku": sku,
        "bike_model": bom["bike_model"],
        "volume": volume,
        "unique_suppliers_used": sorted(suppliers_used),
        "single_source_part_count": len(parts_list["parts"]),
        "total_part_count": len(parts_list["parts"]),
        "geographic_concentration_pct_by_country": geographic_concentration,
        "top_country": top_country,
        "top_country_pct": top_country_pct,
        "capacity_risk_suppliers": capacity_risk_suppliers,
        "reliability_by_supplier": reliability_by_supplier,
        "low_reliability_suppliers": low_reliability_suppliers,
        "critical_path_supplier_id": critical_supplier_id,
        "critical_path_supplier_reliability": critical_reliability,
        "critical_path_lead_days": critical_lead_days,
        "schedule_buffer_days": buffer_days,
        "schedule_buffer_pct": buffer_pct,
        "thin_schedule_buffer": thin_schedule_buffer,
        "risk_flags": sorted(risk_flags),
    }


if __name__ == "__main__":
    import json
    data = load_all()
    for sku in data["all_skus"]:
        pl = parts_list_golden(sku)
        risk = supply_risk_golden(sku, volume=2000)
        print(f"{sku}: parts_ok total=${pl['total_parts_cost_usd']:.2f} | "
              f"risk_flags={risk['risk_flags']}")
