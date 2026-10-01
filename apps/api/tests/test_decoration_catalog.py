from app.game_data.decoration_catalog import DECORATION_BY_KEY, DECORATIONS


def test_alpha_decoration_catalog_has_required_content_volume():
    assert len(DECORATIONS) == 40
    assert len(DECORATION_BY_KEY) == 40
    assert len({item.category for item in DECORATIONS}) >= 6
    assert all(item.cost_cash > 0 for item in DECORATIONS)
    assert all(item.min_level > 0 for item in DECORATIONS)
