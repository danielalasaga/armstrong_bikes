"""Builds concrete test scenarios (SKU x volume x deadline) from real data.

Volume tiers are derived per-SKU from the tightest supplier capacity actually
used in that bike's BOM, not hardcoded — a fixed "6000 units" scenario would
be meaningless for one bike and a non-event for another given how much
capacity varies across the 10 suppliers (15,000/yr for AlpineShox vs.
500,000/yr for FastenRight). Deriving tiers keeps the "stress" scenario
actually stressful for every SKU.
"""
from __future__ import annotations

from data_loader import load_all
from golden import parts_list_golden, cost_leadtime_golden, extract_supplier_id


def _tightest_supplier_capacity(sku: str) -> float:
    """The effective per-bike order volume that would exactly exhaust the
    tightest supplier's annual capacity, accounting for suppliers that
    provide MULTIPLE parts on this bike (e.g. SteelPath supplies all 7
    drivetrain parts on the MTB — its true per-bike demand is 7x volume, not
    1x). Using a supplier's raw annual_capacity_units without that would
    understate how many units you can actually order before hitting them."""
    data = load_all()
    parts = parts_list_golden(sku)["parts"]
    qty_per_bike_by_supplier: dict[str, int] = {}
    for p in parts:
        qty_per_bike_by_supplier[p["supplier_id"]] = qty_per_bike_by_supplier.get(p["supplier_id"], 0) + p["qty"]
    effective_capacities = [
        data["suppliers_by_id"][sid]["annual_capacity_units"] / qty_per_bike
        for sid, qty_per_bike in qty_per_bike_by_supplier.items()
    ]
    return min(effective_capacities)


def volume_tiers(sku: str) -> dict:
    """Three order-volume tiers per SKU, sized off the tightest supplier
    capacity actually used in that bike's BOM:
      - safe:       comfortably within capacity, should read as low-risk
      - stress:     past the concentration-warning threshold but still
                    technically fulfillable (see CAPACITY_CONCENTRATION_WARN_PCT)
      - overcommit: past 100% of capacity — genuinely infeasible as ordered
    """
    tightest = _tightest_supplier_capacity(sku)
    return {
        "safe": max(100, round(tightest * 0.20)),
        "stress": round(tightest * 0.85),
        "overcommit": round(tightest * 1.30),
    }


def critical_path_overcommit_volume(sku: str) -> int:
    """Volume sized to exceed the CRITICAL-PATH supplier's own raw capacity
    specifically (not the aggregate cross-supplier bottleneck used by
    volume_tiers/supply_risk) — this is the right denominator for
    cost_leadtime_golden's `capacity_infeasible`, which is scoped to that one
    supplier. The critical-path supplier and the aggregate-tightest supplier
    are often different (e.g. MTB's critical path is AlpineShox's fork, but
    SteelPath's 7 drivetrain parts are the tighter aggregate constraint) —
    conflating the two under-sizes this scenario and silently stops testing
    the infeasible case."""
    data = load_all()
    assembly = data["assembly_by_sku"][sku]
    critical_supplier_id = extract_supplier_id(assembly["supplier_lead_times"]["critical_path_supplier"])
    capacity = data["suppliers_by_id"][critical_supplier_id]["annual_capacity_units"]
    return round(capacity * 1.30)


def deadline_scenarios(sku: str, volume: int) -> dict:
    """Three assembly-deadline scenarios keyed off this SKU's real
    total_d2c_fulfillment_days_max: comfortable, boundary (exactly on time),
    and late (should be flagged as missed)."""
    baseline = cost_leadtime_golden(sku, volume=volume, assembly_deadline_day=None)
    max_days = baseline["total_d2c_fulfillment_days_max"]
    return {
        "comfortable": max_days + 10,
        "boundary": max_days,
        "late": max_days - 10,
    }


def all_skus() -> list[str]:
    return load_all()["all_skus"]


if __name__ == "__main__":
    for sku in all_skus():
        tiers = volume_tiers(sku)
        deadlines = deadline_scenarios(sku, tiers["safe"])
        print(f"{sku}: volumes={tiers} deadlines(at safe volume)={deadlines}")
