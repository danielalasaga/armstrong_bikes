from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class SupplierQuote(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "part_name": "Frame",
                "supplier_id": "SUP_A",
                "unit_price": 18.00,
                "currency": "USD",
                "incoterm": "FOB",
                "lead_time_days": 28,
                "moq": 2000,
            }
        }
    )

    part_name: str = Field(
        description="Part name matching the BOM (e.g. 'Frame', 'Wheels', 'Derailleur')."
    )
    supplier_id: str = Field(
        description="Caller-defined supplier identifier. Used to cross-reference results."
    )
    unit_price: float = Field(
        gt=0,
        description="Price per unit in the stated currency.",
    )
    currency: str = Field(
        default="USD",
        description="ISO 4217 currency code. Converted to USD using fixed FX rates.",
    )
    incoterm: Literal["FOB", "CIF", "DDP", "EXW", "FCA"] = Field(
        description=(
            "Delivery terms. Determines which cost components (freight, duty, insurance) "
            "the buyer must add on top of the unit price."
        )
    )
    lead_time_days: int = Field(
        gt=0,
        description="Days from order placement to arrival at the destination port.",
    )
    moq: int = Field(
        default=1,
        ge=1,
        description="Minimum order quantity. A surcharge applies if volume is below MOQ.",
    )


class RFQRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "rfq_id": "RFQ-005",
                "bike_model": "Commuter",
                "volume": 6000,
                "assembly_deadline_day": 30,
                "optimization_strategy": "greedy",
                "supplier_quotes": [
                    {
                        "part_name": "Frame",
                        "supplier_id": "SUP_A",
                        "unit_price": 18.00,
                        "currency": "USD",
                        "incoterm": "FOB",
                        "lead_time_days": 28,
                        "moq": 2000,
                    },
                    {
                        "part_name": "Wheels",
                        "supplier_id": "SUP_C",
                        "unit_price": 13.50,
                        "currency": "USD",
                        "incoterm": "CIF",
                        "lead_time_days": 22,
                        "moq": 5000,
                    },
                ],
            }
        }
    )

    rfq_id: str | None = Field(
        default=None,
        description="Optional caller-supplied ID. Auto-generated UUID if omitted.",
    )
    bike_model: Literal["Commuter", "Mountain", "Road"] = Field(
        description="Bike model to source. Determines BOM parts list and assembly time."
    )
    volume: int = Field(
        gt=0,
        description="Number of bikes to produce in this production run.",
    )
    assembly_deadline_day: int = Field(
        gt=0,
        description=(
            "Day number (from Day 0 = order placement) by which all bikes must be "
            "assembled and ready for shipment."
        ),
    )
    optimization_strategy: Literal["greedy", "consolidation", "balanced"] = Field(
        default="greedy",
        description=(
            "Cost optimization approach. 'greedy': cheapest supplier per part. "
            "'consolidation': fewer suppliers for volume discounts. "
            "'balanced': cheapest on non-critical parts, fastest on critical parts."
        ),
    )
    supplier_quotes: list[SupplierQuote] = Field(
        min_length=1,
        description=(
            "Supplier quotes to evaluate. At minimum must include a quote for 'Frame' "
            "(the critical-path bottleneck). Multiple quotes for the same part are "
            "allowed — the cost specialist selects the best."
        ),
    )


class QARequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "question": "Why was the frame supplier chosen over the Taiwan alternative?"
            }
        }
    )

    question: str = Field(
        min_length=1,
        description=(
            "Natural-language question about the completed sourcing memo. "
            "The Q&A agent has full context of all four skill files plus the memo."
        ),
    )


class QAResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "rfq_id": "RFQ-005",
                "question": "Why was the frame supplier chosen over the Taiwan alternative?",
                "answer": "## Frame Supplier Selection\n\nShanghai Steel was selected because...",
                "tokens_used": 310,
            }
        }
    )

    rfq_id: str = Field(description="ID of the RFQ this answer pertains to.")
    question: str = Field(description="The original question, echoed back.")
    answer: str = Field(
        description="Markdown-formatted answer. Pass through marked.parse() before rendering."
    )
    tokens_used: int = Field(description="Tokens consumed by the Q&A agent call.")
