"""Loads the Armstrong Bikes 'Hackathon Data' files and indexes them for lookup.

Data lives one level up from this package, in "../Hackathon Data" (relative to
the armstrong_bike repo clone). This module only reads that data — it never
mutates it — so it's safe to import from golden.py, scenarios.py, and agents.py
alike.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from functools import lru_cache

DATA_DIR = Path(__file__).resolve().parent.parent / "Hackathon Data"


def _load(filename: str) -> dict:
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(
            f"Expected Hackathon Data file not found: {path}\n"
            f"Check that eval_fw/ sits inside the armstrong_bike clone, next to 'Hackathon Data/'."
        )
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_day_range(value) -> tuple[int, int]:
    """'55-59' -> (55, 59). A bare number (int/float/str) -> (n, n)."""
    if isinstance(value, (int, float)):
        return int(value), int(value)
    match = re.match(r"^\s*(\d+)\s*-\s*(\d+)\s*$", str(value))
    if match:
        return int(match.group(1)), int(match.group(2))
    return int(str(value).strip()), int(str(value).strip())


@lru_cache(maxsize=1)
def load_all() -> dict:
    """Loads and cross-indexes every Hackathon Data file. Cached — call freely."""
    bike_models = _load("bike_models.json")["bike_models"]
    part_families = _load("part_families.json")["part_families"]
    parts_catalog = _load("parts_catalog.json")["parts_catalog"]
    bom_data = _load("bill_of_materials.json")["bill_of_materials"]
    suppliers = _load("suppliers.json")["suppliers"]
    assembly_raw = _load("assembly_estimates.json")
    assembly_estimates = assembly_raw["assembly_estimates"]
    assembly_overview = assembly_raw["overview"]

    suppliers_by_id = {s["supplier_id"]: s for s in suppliers}
    parts_by_number = {p["part_number"]: p for p in parts_catalog}
    families_by_code = {f["family_code"]: f for f in part_families}
    bom_by_sku = {b["bike_sku"]: b for b in bom_data}
    assembly_by_sku = {a["bike_sku"]: a for a in assembly_estimates}
    models_by_sku = {m["sku"]: m for m in bike_models}

    missing_bom = [m["sku"] for m in bike_models if m["sku"] not in bom_by_sku]
    missing_assembly = [m["sku"] for m in bike_models if m["sku"] not in assembly_by_sku]
    if missing_bom:
        raise ValueError(f"bike_models.json has SKUs with no bill_of_materials entry: {missing_bom}")
    if missing_assembly:
        raise ValueError(f"bike_models.json has SKUs with no assembly_estimates entry: {missing_assembly}")

    return {
        "bike_models": bike_models,
        "part_families": part_families,
        "parts_catalog": parts_catalog,
        "bom_data": bom_data,
        "suppliers": suppliers,
        "assembly_estimates": assembly_estimates,
        "assembly_overview": assembly_overview,
        "suppliers_by_id": suppliers_by_id,
        "parts_by_number": parts_by_number,
        "families_by_code": families_by_code,
        "bom_by_sku": bom_by_sku,
        "assembly_by_sku": assembly_by_sku,
        "models_by_sku": models_by_sku,
        "all_skus": [m["sku"] for m in bike_models],
    }


if __name__ == "__main__":
    data = load_all()
    print(f"Loaded {len(data['bike_models'])} bike models, {len(data['parts_catalog'])} catalog parts, "
          f"{len(data['suppliers'])} suppliers.")
    for sku in data["all_skus"]:
        bom = data["bom_by_sku"][sku]
        print(f"  {sku}: {bom['bike_model']} — {bom['total_part_lines']} lines, "
              f"${bom['total_parts_cost_usd']:.2f}/unit parts cost, "
              f"critical path {bom['critical_path_part']} ({bom['critical_path_lead_days']}d)")
