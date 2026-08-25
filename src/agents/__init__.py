from __future__ import annotations
from functools import lru_cache
from pathlib import Path

SKILL_FILES = {
    "bom": "bom-structure.md",
    "cost": "cost-optimizer.md",
    "lead_time": "lead-time-critical-path.md",
    "recommendation": "sourcing-recommendation.md",
}


@lru_cache(maxsize=None)
def load_skill(skill_key: str, skills_dir: str) -> str:
    filename = SKILL_FILES[skill_key]
    path = Path(skills_dir) / filename
    return path.read_text(encoding="utf-8")


def load_all_skills(skills_dir: str) -> dict[str, str]:
    return {key: load_skill(key, skills_dir) for key in SKILL_FILES}
