from app.game_data.production_catalog import STARTER_VARIETIES, STARTER_VARIETY_BY_KEY


def test_alpha_varieties_are_data_driven_and_level_gated():
    assert len(STARTER_VARIETIES) == 10
    assert len(STARTER_VARIETY_BY_KEY) == 10
    assert [variety.key for variety in STARTER_VARIETIES[:3]] == [
        "aurora-drift",
        "ember-leaf",
        "moon-sprout",
    ]
    assert STARTER_VARIETY_BY_KEY["quiet-thunder"].min_level == 16
    assert all(variety.grow_seconds > 0 for variety in STARTER_VARIETIES)
    assert all(variety.base_yield > 0 for variety in STARTER_VARIETIES)
    assert all(variety.min_level > 0 for variety in STARTER_VARIETIES)
