import json
from importlib import resources


def test_starter_varieties_are_data_driven_and_valid():
    raw = resources.files("app.game_data").joinpath("starter_varieties.json").read_text()
    records = json.loads(raw)

    assert [record["key"] for record in records] == [
        "aurora-drift",
        "ember-leaf",
        "moon-sprout",
    ]
    assert len({record["key"] for record in records}) == 3
    assert all(record["grow_seconds"] > 0 for record in records)
    assert all(record["base_yield"] > 0 for record in records)
