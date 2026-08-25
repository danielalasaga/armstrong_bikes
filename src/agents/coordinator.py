from __future__ import annotations
import anthropic
from typing import AsyncGenerator
from ..models.rfq import RFQRequest
from ..models.memo import (
    CostAnalysis, LeadTimeAnalysis, CoordinatorDecision, CompletedRFQ,
)
from ..models.events import SourcingEvent, EventType
from ..data.loader import ReferenceData
from .cost_specialist import run_cost_specialist
from .lead_time_specialist import run_lead_time_specialist
from .output_formatter import run_output_formatter

# Cost delta threshold: if switching the bottleneck supplier costs <5% more
# than the total BOM, it's worth paying to hit the deadline.
SWAP_THRESHOLD = 0.05


def _apply_decision_tree(
    cost_analysis: CostAnalysis,
    lead_time: LeadTimeAnalysis,
) -> CoordinatorDecision:
    if lead_time.on_time:
        if lead_time.days_early >= 3:
            return CoordinatorDecision(
                decision="accept",
                reasoning=(
                    f"Cost-optimised plan is on time with {lead_time.days_early} day(s) "
                    f"margin. No trade-off needed. Total program cost: "
                    f"${cost_analysis.total_program_cost:,.2f}."
                ),
            )
        return CoordinatorDecision(
            decision="accept_with_warning",
            reasoning=(
                f"Plan is on time but margin is tight ({lead_time.days_early} day(s)). "
                f"Accepting cost plan; monitor {lead_time.critical_path_part} closely "
                f"for any delays."
            ),
        )

    # Late — evaluate swapping the bottleneck supplier
    ba = lead_time.bottleneck_analysis
    days_late = lead_time.days_late
    bottleneck = lead_time.critical_path_part

    if (
        ba.fastest_alternative_total_cost_delta is not None
        and ba.fastest_alternative_total_cost_delta
        < SWAP_THRESHOLD * cost_analysis.total_program_cost
    ):
        return CoordinatorDecision(
            decision="swap_bottleneck",
            bottleneck_part=bottleneck,
            cost_delta_per_unit=ba.fastest_alternative_cost_delta_per_unit,
            total_cost_delta=ba.fastest_alternative_total_cost_delta,
            reasoning=(
                f"Plan is {days_late} day(s) late. Bottleneck: {bottleneck}. "
                f"Switching to faster supplier adds "
                f"${ba.fastest_alternative_total_cost_delta:,.2f} "
                f"(<{SWAP_THRESHOLD*100:.0f}% of total BOM). Accepted to hit deadline."
            ),
        )

    return CoordinatorDecision(
        decision="deadline_at_risk",
        bottleneck_part=bottleneck,
        cost_delta_per_unit=ba.fastest_alternative_cost_delta_per_unit,
        total_cost_delta=ba.fastest_alternative_total_cost_delta,
        reasoning=(
            f"Plan is {days_late} day(s) late. Bottleneck: {bottleneck}. "
            f"Cost to expedite exceeds {SWAP_THRESHOLD*100:.0f}% of total BOM or no "
            f"faster supplier available. Deadline at risk — recommend extending deadline "
            f"or sourcing review."
        ),
    )


async def run_coordinator(
    rfq: RFQRequest,
    reference_data: ReferenceData,
    skills: dict[str, str],
    client: anthropic.AsyncAnthropic,
) -> AsyncGenerator[SourcingEvent, None]:

    rfq_id = rfq.rfq_id or "unknown"

    yield SourcingEvent(
        event=EventType.RFQ_STARTED,
        rfq_id=rfq_id,
        payload={
            "bike_model": rfq.bike_model,
            "volume": rfq.volume,
            "assembly_deadline_day": rfq.assembly_deadline_day,
            "quote_count": len(rfq.supplier_quotes),
        },
    )

    # Step 1 — Cost specialist (Haiku 4.5)
    try:
        cost_analysis = await run_cost_specialist(
            rfq, reference_data, skills["cost"], client
        )
    except Exception as exc:
        yield SourcingEvent(
            event=EventType.ERROR,
            rfq_id=rfq_id,
            payload={"stage": "cost_specialist", "message": str(exc)},
        )
        return

    yield SourcingEvent(
        event=EventType.COST_ANALYSIS_COMPLETE,
        rfq_id=rfq_id,
        payload=cost_analysis.model_dump(),
    )

    # Step 2 — Lead-time specialist (Haiku 4.5)
    try:
        lead_time = await run_lead_time_specialist(
            cost_analysis, rfq.assembly_deadline_day, skills["lead_time"], client
        )
    except Exception as exc:
        yield SourcingEvent(
            event=EventType.ERROR,
            rfq_id=rfq_id,
            payload={"stage": "lead_time_specialist", "message": str(exc)},
        )
        return

    yield SourcingEvent(
        event=EventType.LEAD_TIME_ANALYSIS_COMPLETE,
        rfq_id=rfq_id,
        payload=lead_time.model_dump(),
    )

    # Step 3 — Pure-Python decision tree (no LLM call)
    decision = _apply_decision_tree(cost_analysis, lead_time)

    # If bottleneck swap warranted, re-run cost specialist for the faster supplier
    if decision.decision == "swap_bottleneck" and decision.bottleneck_part:
        try:
            cost_analysis = await run_cost_specialist(
                rfq, reference_data, skills["cost"], client,
                bottleneck_part=decision.bottleneck_part,
            )
            # Recalculate decision with updated cost (swap already chosen)
            decision = CoordinatorDecision(
                decision="swap_bottleneck",
                bottleneck_part=decision.bottleneck_part,
                cost_delta_per_unit=decision.cost_delta_per_unit,
                total_cost_delta=decision.total_cost_delta,
                reasoning=decision.reasoning + " Updated cost plan reflects faster supplier.",
            )
        except Exception as exc:
            yield SourcingEvent(
                event=EventType.ERROR,
                rfq_id=rfq_id,
                payload={"stage": "cost_specialist_swap", "message": str(exc)},
            )
            return

    yield SourcingEvent(
        event=EventType.COORDINATOR_DECISION,
        rfq_id=rfq_id,
        payload=decision.model_dump(),
    )

    # Step 4 — Output formatter (Sonnet 4.6)
    try:
        memo = await run_output_formatter(
            cost_analysis, lead_time, decision, skills["recommendation"], client
        )
    except Exception as exc:
        yield SourcingEvent(
            event=EventType.ERROR,
            rfq_id=rfq_id,
            payload={"stage": "output_formatter", "message": str(exc)},
        )
        return

    yield SourcingEvent(
        event=EventType.MEMO_COMPLETE,
        rfq_id=rfq_id,
        payload=memo.model_dump(),
    )
