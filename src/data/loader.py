from __future__ import annotations
import json
import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path


@dataclass
class ReferenceData:
    suppliers: list[dict] = field(default_factory=list)
    duty_rates: list[dict] = field(default_factory=list)
    freight_rates: list[dict] = field(default_factory=list)
    fx_rates: dict = field(default_factory=dict)

    def get_supplier(self, supplier_id: str) -> dict | None:
        return next((s for s in self.suppliers if s["supplier_id"] == supplier_id), None)

    def get_freight_rate(self, origin_country: str, mode: str = "sea") -> dict | None:
        return next(
            (r for r in self.freight_rates
             if r["origin_country"] == origin_country and r["mode"] == mode),
            None,
        )

    def get_duty_rate(self, part_category: str, material: str | None = None) -> float:
        candidates = [r for r in self.duty_rates if r["part_category"] == part_category]
        if material:
            exact = next((r for r in candidates if r.get("material") == material), None)
            if exact:
                return exact["duty_rate"]
        if candidates:
            return candidates[0]["duty_rate"]
        return 0.025  # conservative default

    def convert_to_usd(self, amount: float, currency: str) -> float:
        rate = self.fx_rates.get("rates", {}).get(currency.upper(), 1.0)
        return amount * rate


@lru_cache(maxsize=1)
def load_reference_data(data_dir: str) -> ReferenceData:
    base = Path(data_dir)
    with open(base / "suppliers.json") as f:
        suppliers = json.load(f)
    with open(base / "duty_rates.json") as f:
        duty_rates = json.load(f)
    with open(base / "freight_rates.json") as f:
        freight_rates = json.load(f)
    with open(base / "fx_rates.json") as f:
        fx_rates = json.load(f)
    return ReferenceData(
        suppliers=suppliers,
        duty_rates=duty_rates,
        freight_rates=freight_rates,
        fx_rates=fx_rates,
    )
