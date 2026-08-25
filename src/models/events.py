from __future__ import annotations
from enum import Enum
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class EventType(str, Enum):
    """All SSE event names emitted by POST /api/v1/rfq in the order they are sent."""

    RFQ_STARTED = "rfq_started"
    COST_ANALYSIS_COMPLETE = "cost_analysis_complete"
    LEAD_TIME_ANALYSIS_COMPLETE = "lead_time_analysis_complete"
    COORDINATOR_DECISION = "coordinator_decision"
    MEMO_COMPLETE = "memo_complete"
    ERROR = "error"


class SourcingEvent(BaseModel):
    """
    Envelope for every SSE event. Each line in the stream is:
        data: {SourcingEvent as JSON}\\n\\n
    The stream terminates with:
        data: [DONE]\\n\\n
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "event": "cost_analysis_complete",
                "rfq_id": "RFQ-005",
                "payload": {
                    "bike_model": "Commuter",
                    "volume": 6000,
                    "total_bom_cost_per_bike": 137.03,
                },
            }
        }
    )

    event: EventType = Field(
        description=(
            "Event name. Consumers should switch on this field to determine "
            "how to deserialise payload."
        )
    )
    rfq_id: str = Field(description="ID of the RFQ this event belongs to.")
    payload: dict[str, Any] = Field(
        description=(
            "Event-specific data. Shape per event:\n"
            "  rfq_started              → {bike_model, volume, assembly_deadline_day, quote_count}\n"
            "  cost_analysis_complete   → CostAnalysis\n"
            "  lead_time_analysis_complete → LeadTimeAnalysis\n"
            "  coordinator_decision     → CoordinatorDecision\n"
            "  memo_complete            → MemoOutput\n"
            "  error                    → {stage: str, message: str}"
        )
    )


# ---------------------------------------------------------------------------
# Typed payload schemas for each event — used for documentation and validation
# when the frontend or tests need to parse a specific event's payload.
# ---------------------------------------------------------------------------

class RFQStartedPayload(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "bike_model": "Commuter",
                "volume": 6000,
                "assembly_deadline_day": 30,
                "quote_count": 4,
            }
        }
    )

    bike_model: str = Field(description="Bike model from the RFQ.")
    volume: int = Field(description="Production volume from the RFQ.")
    assembly_deadline_day: int = Field(description="Assembly deadline day from the RFQ.")
    quote_count: int = Field(description="Number of supplier quotes submitted.")


class ErrorPayload(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "stage": "cost_specialist",
                "message": "Failed to parse JSON from model response",
            }
        }
    )

    stage: str = Field(
        description=(
            "Pipeline stage that failed. One of: "
            "cost_specialist, lead_time_specialist, "
            "cost_specialist_swap, output_formatter, stream."
        )
    )
    message: str = Field(description="Error message.")


class HealthResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "ok",
                "reference_data_loaded": True,
                "skills_loaded": ["bom", "cost", "lead_time", "recommendation"],
            }
        }
    )

    status: Literal["ok", "degraded"] = Field(
        description="ok if all reference data and skills loaded successfully."
    )
    reference_data_loaded: bool = Field(
        description="True if all four data/*.json files were read at startup."
    )
    skills_loaded: list[str] = Field(
        description="Keys of skill files successfully read (bom, cost, lead_time, recommendation)."
    )
