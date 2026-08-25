from __future__ import annotations
import json
import anthropic
from ..models.memo import CompletedRFQ
from ..config import settings


def _build_system_prompt(completed_rfq: CompletedRFQ, all_skills: dict[str, str]) -> str:
    skills_block = "\n\n---\n\n".join(
        f"# SKILL: {key.upper()}\n\n{text}" for key, text in all_skills.items()
    )
    memo_block = ""
    if completed_rfq.memo:
        memo_block = (
            "\n\n---\n\n# COMPLETED SOURCING MEMO (JSON)\n\n"
            + json.dumps(completed_rfq.memo.json_memo, indent=2)
        )
    cost_block = ""
    if completed_rfq.cost_analysis:
        cost_block = (
            "\n\n---\n\n# COST ANALYSIS\n\n"
            + json.dumps(completed_rfq.cost_analysis.model_dump(), indent=2)
        )
    lead_block = ""
    if completed_rfq.lead_time_analysis:
        lead_block = (
            "\n\n---\n\n# LEAD-TIME ANALYSIS\n\n"
            + json.dumps(completed_rfq.lead_time_analysis.model_dump(), indent=2)
        )
    decision_block = ""
    if completed_rfq.coordinator_decision:
        decision_block = (
            "\n\n---\n\n# COORDINATOR DECISION\n\n"
            + json.dumps(completed_rfq.coordinator_decision.model_dump(), indent=2)
        )

    return (
        "You are a procurement expert assistant. Answer the user's question about the "
        "completed sourcing decision below. Be concise, specific, and cite the relevant "
        "data from the analyses. Format your answer as Markdown.\n\n"
        + skills_block
        + memo_block
        + cost_block
        + lead_block
        + decision_block
    )


async def run_qa_agent(
    question: str,
    completed_rfq: CompletedRFQ,
    all_skills: dict[str, str],
    client: anthropic.AsyncAnthropic,
) -> tuple[str, int]:
    system_prompt = _build_system_prompt(completed_rfq, all_skills)
    response = await client.messages.create(
        model=settings.qa_model,
        max_tokens=2048,
        system=system_prompt,
        messages=[{"role": "user", "content": question}],
    )
    answer = response.content[0].text
    tokens = response.usage.input_tokens + response.usage.output_tokens
    return answer, tokens
