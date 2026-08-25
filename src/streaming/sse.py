from __future__ import annotations
from typing import AsyncGenerator
from ..models.events import SourcingEvent
from ..models.memo import CompletedRFQ


async def event_stream(
    generator: AsyncGenerator[SourcingEvent, None],
    rfq_store: dict[str, CompletedRFQ],
    rfq_id: str,
    bike_model: str,
    volume: int,
) -> AsyncGenerator[str, None]:
    """
    Consume events from the coordinator generator, emit SSE-formatted strings,
    and accumulate completed state into rfq_store.
    """
    from ..models.memo import CostAnalysis, LeadTimeAnalysis, CoordinatorDecision, MemoOutput
    from ..models.events import EventType
    import json
    from datetime import datetime, timezone

    cost_analysis = None
    lead_time_analysis = None
    coordinator_decision = None
    memo = None
    total_tokens = 0
    error_msg = None

    try:
        async for event in generator:
            yield f"data: {event.model_dump_json()}\n\n"

            p = event.payload
            if event.event == EventType.COST_ANALYSIS_COMPLETE:
                cost_analysis = CostAnalysis(**p)
                total_tokens += p.get("tokens_used", 0)
            elif event.event == EventType.LEAD_TIME_ANALYSIS_COMPLETE:
                lead_time_analysis = LeadTimeAnalysis(**p)
                total_tokens += p.get("tokens_used", 0)
            elif event.event == EventType.COORDINATOR_DECISION:
                coordinator_decision = CoordinatorDecision(**p)
            elif event.event == EventType.MEMO_COMPLETE:
                memo = MemoOutput(**p)
            elif event.event == EventType.ERROR:
                error_msg = p.get("message", "Unknown error")

    except Exception as exc:
        error_event = SourcingEvent(
            event=EventType.ERROR,
            rfq_id=rfq_id,
            payload={"stage": "stream", "message": str(exc)},
        )
        yield f"data: {error_event.model_dump_json()}\n\n"
        error_msg = str(exc)

    # Cost per decision (approximate, based on token counts from specialists)
    # Sonnet tokens are estimated for coordinator/formatter (~400 + ~310 tokens)
    cost_per_decision = total_tokens / 1_000_000 * 3.0

    rfq_store[rfq_id] = CompletedRFQ(
        rfq_id=rfq_id,
        status="error" if error_msg else "complete",
        bike_model=bike_model,
        volume=volume,
        cost_analysis=cost_analysis,
        lead_time_analysis=lead_time_analysis,
        coordinator_decision=coordinator_decision,
        memo=memo,
        tokens_used_total=total_tokens,
        cost_per_decision_usd=round(cost_per_decision, 4),
        completed_at=datetime.now(timezone.utc).isoformat(),
        error=error_msg,
    )

    yield "data: [DONE]\n\n"
