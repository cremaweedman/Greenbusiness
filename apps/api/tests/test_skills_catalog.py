from __future__ import annotations

from app.game_data.skills_catalog import SKILL_BRANCHES, SKILL_BY_KEY, SKILLS, SKILLS_CATALOG


def test_skill_catalog_is_versioned_and_covers_three_branches():
    assert SKILLS_CATALOG.version == "p3-skills-v1"
    assert {skill.branch for skill in SKILLS} == SKILL_BRANCHES
    assert len(SKILL_BY_KEY) == len(SKILLS)


def test_starter_skills_have_real_small_effects():
    botany = SKILL_BY_KEY["botany-careful-hands"]
    commerce = SKILL_BY_KEY["commerce-counter-presence"]
    operations = SKILL_BY_KEY["operations-fast-setup"]

    assert botany.effects.care_yield_bonus == 1
    assert commerce.effects.contract_cash_bonus == 10
    assert operations.effects.grow_seconds_reduction == 15
    assert all(skill.cost_per_rank == 1 and skill.max_rank == 1 for skill in SKILLS)
