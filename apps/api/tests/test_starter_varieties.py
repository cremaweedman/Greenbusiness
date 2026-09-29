from app.game_data.production_catalog import STARTER_VARIETIES, STARTER_VARIETY_BY_KEY


def test_starter_varieties_are_data_driven_and_valid():
    assert [variety.key for variety in STARTER_VARIETIES] == [
        "aurora-drift",
        "ember-leaf",
        "moon-sprout",
    ]
    assert len(STARTER_VARIETY_BY_KEY) == 3
    assert all(variety.grow_seconds > 0 for variety in STARTER_VARIETIES)
    assert all(variety.base_yield > 0 for variety in STARTER_VARIETIES)
