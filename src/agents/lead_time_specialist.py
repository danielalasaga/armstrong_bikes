from __future__ import annotations
import json
import re
import anthropic
from ..models.memo import CostAnalysis, LeadTimeAnalysis
from ..config import settings


def _extract_json(text: str) -> str:
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        return match.group(1)
    start = text.find("{")
    end = text.rfind("}") + 1
    if start >= 0 and end > start:
        return text[start:end]
    raise ValueError("No JSON object found in response")


async def run_lead_time_specialist(
    cost_analysis: CostAnalysis,
    assembly_deadline_day: int,
    skill_text: str,
    client: anthropic.AsyncAnthropic,
) -> LeadTimeAnalysis:
    user_msg = json.dumps(
        {
            "task": (
                "Analyse the sourcing plan below against the assembly deadline. "
                "Identify the critical path, bottleneck part, and determine whether "
                "delivery is on time. Return ONLY the JSON object defined in the "
                "Output Format section of your instructions. "
                "Do not include any explanation outside the JSON."
            ),
            "bike_model": cost_analysis.bike_model,
            "volume": cost_analysis.volume,
            "assembly_deadline_day": assembly_deadline_day,
            "sourcing_plan": [line.model_dump() for line in cost_analysis.sourcing_plan],
        },
        indent=2,
    )

    response = await client.messages.create(
        model=settings.specialist_model,
        max_tokens=4096,
        system=skill_text,
        messages=[{"role": "user", "content": user_msg}],
    )
    raw = response.content[0].text
    parsed = json.loads(_extract_json(raw))
    parsed["tokens_used"] = response.usage.input_tokens + response.usage.output_tokens
    return LeadTimeAnalysis(**parsed)
