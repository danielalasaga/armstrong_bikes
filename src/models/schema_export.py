"""
Export all contract models as JSON Schema.

Usage:
    python -m src.models.schema_export            # prints to stdout
    python -m src.models.schema_export > schema.json
"""
from __future__ import annotations
import json
from pydantic import BaseModel
from . import (
    SupplierQuote,
    RFQRequest,
    QARequest,
    QAResponse,
    PartCostLine,
    CostAnalysis,
    PartLeadTimeLine,
    BottleneckAnalysis,
    LeadTimeAnalysis,
    CoordinatorDecision,
    MemoOutput,
    CompletedRFQ,
    SourcingEvent,
    RFQStartedPayload,
    ErrorPayload,
    HealthResponse,
)

# All models in the contract, grouped by concern
CONTRACT_MODELS: dict[str, type[BaseModel]] = {
    # --- Request models ---
    "SupplierQuote": SupplierQuote,
    "RFQRequest": RFQRequest,
    "QARequest": QARequest,
    # --- Response models ---
    "QAResponse": QAResponse,
    "HealthResponse": HealthResponse,
    # --- Agent output sub-models ---
    "PartCostLine": PartCostLine,
    "CostAnalysis": CostAnalysis,
    "PartLeadTimeLine": PartLeadTimeLine,
    "BottleneckAnalysis": BottleneckAnalysis,
    "LeadTimeAnalysis": LeadTimeAnalysis,
    "CoordinatorDecision": CoordinatorDecision,
    "MemoOutput": MemoOutput,
    "CompletedRFQ": CompletedRFQ,
    # --- SSE event models ---
    "SourcingEvent": SourcingEvent,
    "RFQStartedPayload": RFQStartedPayload,
    "ErrorPayload": ErrorPayload,
}


def export_schema() -> dict:
    """
    Returns a dict with one JSON Schema definition per model.
    Compatible with OpenAPI 3.1 $defs / components/schemas.
    """
    return {
        name: model.model_json_schema()
        for name, model in CONTRACT_MODELS.items()
    }


def export_openapi_components() -> dict:
    """
    Returns the schemas dict formatted for use as the
    components/schemas section of an OpenAPI 3.1 document.
    """
    return {"components": {"schemas": export_schema()}}


if __name__ == "__main__":
    print(json.dumps(export_schema(), indent=2))
