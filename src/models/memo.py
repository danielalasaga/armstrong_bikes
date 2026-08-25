from __future__ import annotations
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field


class PartCostLine(BaseModel):
    """One row in the cost analysis table — one part from one supplier."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "part_name": "Frame",
                "supplier_id": "SUP_A",
                "supplier_name": "Shanghai Steel Co",
                "unit_price_quote": 18.00,
                "currency": "USD",
                "incoterm": "FOB",
                "freight_cost": 0.21,
                "duty_rate": 0.025,
                "insurance_rate": 0.005,
                "landed_cost_per_unit": 17.26,
                "volume": 6000,
                "total_part_cost": 103542.00,
                "lead_time_days": 28,
                "notes": "Volume discount applied at 6,000 units",
            }
        }
    )

    part_name: str = Field(description="Part name (e.g. 'Frame', 'Wheels').")
    supplier_id: str = Field(description="Supplier identifier from the original quote.")
    supplier_name: str = Field(description="Human-readable supplier name.")
    unit_price_quote: float = Field(description="Original quoted price per unit.")
    currency: str = Field(description="ISO 4217 currency of the original quote.")
    incoterm: str = Field(description="Delivery terms from the original quote.")
    freight_cost: float = Field(description="Freight added per unit (0 for CIF/DDP).")
    duty_rate: float = Field(description="Import duty rate applied (e.g. 0.025 = 2.5%).")
    insurance_rate: float = Field(description="Insurance rate applied (e.g. 0.005 = 0.5%).")
    landed_cost_per_unit: float = Field(
        description="Total all-in cost per unit in USD after freight, duty, and insurance."
    )
    volume: int = Field(description="Units ordered from this supplier for this part.")
    total_part_cost: float = Field(
        description="landed_cost_per_unit × volume for this part line."
    )
    lead_time_days: int = Field(description="Supplier lead time in days.")
    notes: str = Field(default="", description="Volume discount or other notes.")


class CostAnalysis(BaseModel):
    """Full output from the Cost Specialist agent."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "bike_model": "Commuter",
                "volume": 6000,
                "sourcing_plan": [],
                "total_bom_cost_per_bike": 137.03,
                "total_program_cost": 822180.00,
                "cost_vs_next_alternative": -5200.00,
                "tokens_used": 1100,
            }
        }
    )

    bike_model: str = Field(description="Bike model this analysis applies to.")
    volume: int = Field(description="Production volume.")
    sourcing_plan: list[PartCostLine] = Field(
        description="One PartCostLine per part in the BOM, each assigned to one supplier."
    )
    total_bom_cost_per_bike: float = Field(
        description="Sum of landed_cost_per_unit across all parts for a single bike."
    )
    total_program_cost: float = Field(
        description="total_bom_cost_per_bike × volume."
    )
    cost_vs_next_alternative: float = Field(
        description=(
            "Dollar difference vs. the next-cheapest sourcing plan. "
            "Negative means this plan is cheaper."
        )
    )
    tokens_used: int = Field(description="Tokens consumed by the Cost Specialist call.")


class PartLeadTimeLine(BaseModel):
    """One row in the lead-time analysis table."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "part_name": "Frame",
                "supplier_id": "SUP_A",
                "lead_time_days": 28,
                "arrival_date_day": 28,
                "criticality": "CRITICAL",
            }
        }
    )

    part_name: str = Field(description="Part name.")
    supplier_id: str = Field(description="Supplier identifier.")
    lead_time_days: int = Field(description="Supplier lead time in days.")
    arrival_date_day: int = Field(
        description="Day number (from Day 0) when this part arrives at the factory."
    )
    criticality: Literal["CRITICAL", "NON_CRITICAL"] = Field(
        description=(
            "CRITICAL parts gate assembly start. "
            "NON_CRITICAL parts (cables, accessories) can arrive after assembly begins."
        )
    )


class BottleneckAnalysis(BaseModel):
    """Identifies the critical-path bottleneck and the fastest available alternative."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "bottleneck_part": "Frame",
                "bottleneck_lead_time": 28,
                "fastest_alternative_supplier": "SUP_B",
                "fastest_alternative_lead_time": 18,
                "fastest_alternative_cost_delta_per_unit": 2.24,
                "fastest_alternative_total_cost_delta": 13440.00,
                "recommendation": "Not needed; on time with current plan",
            }
        }
    )

    bottleneck_part: str = Field(
        description="The part with the longest lead time on the critical path."
    )
    bottleneck_lead_time: int = Field(
        description="Lead time in days for the bottleneck part."
    )
    fastest_alternative_supplier: str | None = Field(
        default=None,
        description="Supplier ID of the fastest available alternative. Null if none exists.",
    )
    fastest_alternative_lead_time: int | None = Field(
        default=None,
        description="Lead time in days for the fastest alternative. Null if none exists.",
    )
    fastest_alternative_cost_delta_per_unit: float | None = Field(
        default=None,
        description=(
            "Additional cost per unit vs. the bottleneck supplier. "
            "Null if no alternative exists."
        ),
    )
    fastest_alternative_total_cost_delta: float | None = Field(
        default=None,
        description=(
            "fastest_alternative_cost_delta_per_unit × volume. "
            "Null if no alternative exists."
        ),
    )
    recommendation: str = Field(
        description="Plain-English recommendation from the Lead-Time Specialist."
    )


class LeadTimeAnalysis(BaseModel):
    """Full output from the Lead-Time Specialist agent."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "bike_model": "Commuter",
                "volume": 6000,
                "assembly_deadline_day": 30,
                "sourcing_plan_lead_times": [],
                "critical_path_part": "Frame",
                "critical_path_arrival_day": 28,
                "assembly_can_start_day": 28,
                "assembly_duration_days": 2,
                "all_bikes_ready_day": 30,
                "on_time": True,
                "days_late": 0,
                "days_early": 2,
                "bottleneck_analysis": {},
                "tokens_used": 850,
            }
        }
    )

    bike_model: str = Field(description="Bike model this analysis applies to.")
    volume: int = Field(description="Production volume.")
    assembly_deadline_day: int = Field(
        description="Day by which all bikes must be assembled (from the RFQ)."
    )
    sourcing_plan_lead_times: list[PartLeadTimeLine] = Field(
        description="One row per part, showing arrival day and criticality."
    )
    critical_path_part: str = Field(
        description="The part that gates assembly start (latest arrival among critical parts)."
    )
    critical_path_arrival_day: int = Field(
        description="Day the critical-path part arrives."
    )
    assembly_can_start_day: int = Field(
        description="Day assembly can begin (= critical_path_arrival_day + inspection buffer)."
    )
    assembly_duration_days: int = Field(
        description="Calendar days needed to assemble the full volume."
    )
    all_bikes_ready_day: int = Field(
        description="assembly_can_start_day + assembly_duration_days."
    )
    on_time: bool = Field(
        description="True if all_bikes_ready_day ≤ assembly_deadline_day."
    )
    days_late: int = Field(
        description="all_bikes_ready_day − assembly_deadline_day when positive; else 0."
    )
    days_early: int = Field(
        description="assembly_deadline_day − all_bikes_ready_day when positive; else 0."
    )
    bottleneck_analysis: BottleneckAnalysis = Field(
        description="Bottleneck identification and fastest-alternative costing."
    )
    tokens_used: int = Field(
        description="Tokens consumed by the Lead-Time Specialist call."
    )


class CoordinatorDecision(BaseModel):
    """
    Pure-Python decision tree output. No LLM call — derived from CostAnalysis
    and LeadTimeAnalysis by the coordinator.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "decision": "accept",
                "bottleneck_part": None,
                "cost_delta_per_unit": None,
                "total_cost_delta": None,
                "reasoning": (
                    "Cost-optimised plan is on time with 2 day(s) margin. "
                    "No trade-off needed. Total program cost: $822,180.00."
                ),
            }
        }
    )

    decision: Literal[
        "accept", "accept_with_warning", "swap_bottleneck", "deadline_at_risk"
    ] = Field(
        description=(
            "accept: on time, ≥3 day margin. "
            "accept_with_warning: on time, <3 day margin. "
            "swap_bottleneck: late, but switching bottleneck supplier costs <5% of BOM. "
            "deadline_at_risk: late, no affordable fix available."
        )
    )
    bottleneck_part: str | None = Field(
        default=None,
        description="Populated only when decision is swap_bottleneck or deadline_at_risk.",
    )
    cost_delta_per_unit: float | None = Field(
        default=None,
        description="Additional cost per unit to switch bottleneck supplier. Null otherwise.",
    )
    total_cost_delta: float | None = Field(
        default=None,
        description="cost_delta_per_unit × volume. Null otherwise.",
    )
    reasoning: str = Field(
        description="Plain-English explanation of the decision, included in the memo."
    )


class MemoOutput(BaseModel):
    """Final memo produced by the Output Formatter agent (Sonnet 4.6)."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "json_memo": {
                    "header": {
                        "to": "Procurement Manager",
                        "from": "Sourcing Swarm",
                        "re": "Commuter 6,000-unit Production Run",
                        "date": "2026-08-25",
                    },
                    "executive_summary": "...",
                    "cost_analysis": {},
                    "lead_time_analysis": {},
                    "decision_rationale": "...",
                    "sensitivity_scenarios": [],
                },
                "markdown": "# Sourcing Recommendation Memo\n\n...",
            }
        }
    )

    json_memo: dict[str, Any] = Field(
        description=(
            "Structured memo following the sourcing-recommendation.md schema. "
            "Contains: header, executive_summary, cost_analysis, lead_time_analysis, "
            "decision_rationale, sensitivity_scenarios."
        )
    )
    markdown: str = Field(
        description=(
            "The complete memo as a Markdown string. "
            "Pass through marked.parse() before inserting into the DOM."
        )
    )


class CompletedRFQ(BaseModel):
    """
    Full RFQ result stored in memory after the SSE stream completes.
    Retrieved via GET /api/v1/rfq/{rfq_id}.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "rfq_id": "RFQ-005",
                "status": "complete",
                "bike_model": "Commuter",
                "volume": 6000,
                "cost_analysis": None,
                "lead_time_analysis": None,
                "coordinator_decision": None,
                "memo": None,
                "tokens_used_total": 2180,
                "cost_per_decision_usd": 0.056,
                "completed_at": "2026-08-25T14:32:00Z",
                "error": None,
            }
        }
    )

    rfq_id: str = Field(description="Unique identifier for this sourcing request.")
    status: Literal["complete", "error"] = Field(
        description="complete: all stages succeeded. error: at least one stage failed."
    )
    bike_model: str = Field(description="Bike model from the original request.")
    volume: int = Field(description="Production volume from the original request.")
    cost_analysis: CostAnalysis | None = Field(
        default=None,
        description="Null if the cost specialist stage failed.",
    )
    lead_time_analysis: LeadTimeAnalysis | None = Field(
        default=None,
        description="Null if the lead-time specialist stage failed.",
    )
    coordinator_decision: CoordinatorDecision | None = Field(
        default=None,
        description="Null if decision could not be computed.",
    )
    memo: MemoOutput | None = Field(
        default=None,
        description="Null if the output formatter stage failed.",
    )
    tokens_used_total: int = Field(
        default=0,
        description="Total tokens across all specialist and formatter calls.",
    )
    cost_per_decision_usd: float = Field(
        default=0.0,
        description="Estimated USD cost for this decision based on token usage.",
    )
    completed_at: str = Field(
        default="",
        description="ISO 8601 timestamp when the stream finished.",
    )
    error: str | None = Field(
        default=None,
        description="Error message when status is 'error'. Null on success.",
    )
