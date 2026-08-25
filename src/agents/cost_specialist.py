from __future__ import annotations
import json
import re
import anthropic
from ..models.rfq import RFQRequest
from ..models.memo import CostAnalysis
from ..data.loader import ReferenceData
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


def _build_user_message(rfq: RFQRequest, reference_data: ReferenceData) -> str:
    quotes_payload = [q.model_dump() for q in rfq.supplier_quotes]
    ref_payload = {
        "fx_rates": reference_data.fx_rates,
        "duty_rates": reference_data.duty_rates,
        "freight_rates": reference_data.freight_rates,
        "suppliers_master": reference_data.suppliers,
    }
    return json.dumps(
        {
            "task": (
                "Calculate the landed cost for each supplier quote below and return "
                "the cheapest complete sourcing plan. Use the reference data provided. "
                "Return ONLY the JSON object defined in the Output Format section of your instructions. "
                "Do not include any explanation outside the JSON."
            ),
            "bike_model": rfq.bike_model,
            "volume": rfq.volume,
            "optimization_strategy": rfq.optimization_strategy,
            "supplier_quotes": quotes_payload,
            "reference_data": ref_payload,
        },
        indent=2,
    )


async def run_cost_specialist(
    rfq: RFQRequest,
    reference_data: ReferenceData,
    skill_text: str,
    client: anthropic.AsyncAnthropic,
    bottleneck_part: str | None = None,
) -> CostAnalysis:
    task_override = ""
    if bottleneck_part:
        task_override = (
            f" Focus specifically on the '{bottleneck_part}' part. "
            "For that part, find the fastest available supplier and calculate the cost delta "
            "vs. the currently selected supplier. Return the full sourcing plan JSON with the "
            "faster supplier substituted for the bottleneck part."
        )

    user_msg = _build_user_message(rfq, reference_data)
    if task_override:
        data = json.loads(user_msg)
        data["task"] += task_override
        user_msg = json.dumps(data, indent=2)

    response = await client.messages.create(
        model=settings.specialist_model,
        max_tokens=4096,
        system=skill_text,
        messages=[{"role": "user", "content": user_msg}],
    )
    raw = response.content[0].text
    parsed = json.loads(_extract_json(raw))

    # Inject actual token count from the API response
    parsed["tokens_used"] = response.usage.input_tokens + response.usage.output_tokens
    return CostAnalysis(**parsed)
