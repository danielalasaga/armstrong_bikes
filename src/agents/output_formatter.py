from __future__ import annotations
import json
import re
import anthropic
from ..models.memo import CostAnalysis, LeadTimeAnalysis, CoordinatorDecision, MemoOutput
from ..config import settings


def _extract_outer_json(text: str) -> str:
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        return match.group(1)
    start = text.find("{")
    end = text.rfind("}") + 1
    if start >= 0 and end > start:
        return text[start:end]
    raise ValueError("No JSON object found in response")


async def run_output_formatter(
    cost_analysis: CostAnalysis,
    lead_time_analysis: LeadTimeAnalysis,
    decision: CoordinatorDecision,
    skill_text: str,
    client: anthropic.AsyncAnthropic,
) -> MemoOutput:
    user_msg = json.dumps(
        {
            "task": (
                "Using the sourcing recommendation memo format defined in your instructions, "
                "produce the final sourcing memo for this decision. "
                "Return a JSON object with exactly two keys:\n"
                "  'json_memo': the full structured memo as a JSON object\n"
                "  'markdown': the complete memo formatted as a Markdown string\n"
                "Do not include anything outside the JSON object."
            ),
            "bike_model": cost_analysis.bike_model,
            "volume": cost_analysis.volume,
            "cost_analysis": cost_analysis.model_dump(),
            "lead_time_analysis": lead_time_analysis.model_dump(),
            "coordinator_decision": decision.model_dump(),
        },
        indent=2,
    )

    response = await client.messages.create(
        model=settings.formatter_model,
        max_tokens=8192,
        system=skill_text,
        messages=[{"role": "user", "content": user_msg}],
    )
    raw = response.content[0].text
    parsed = json.loads(_extract_outer_json(raw))
    return MemoOutput(
        json_memo=parsed.get("json_memo", {}),
        markdown=parsed.get("markdown", raw),
    )
