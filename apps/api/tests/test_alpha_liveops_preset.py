import json
from importlib import resources

from app.schemas import LiveOpsConfigPublishRequest


def test_closed_alpha_liveops_preset_matches_admin_publish_schema():
    raw = resources.files("app.game_data").joinpath("liveops_alpha_mini_arc.json").read_text()
    payload = LiveOpsConfigPublishRequest.model_validate(json.loads(raw))

    assert "closed-alpha-night-market" in payload.config.seasons
    assert payload.config.content_toggles["closed_alpha_night_market"] is True
    assert payload.config.contract_multipliers["default_cash"] == 1.1
    assert payload.config.kill_switches["production"] is False
    assert payload.config.experiments["alpha-timer-copy"] == [
        "control",
        "absolute-ready-emphasis",
    ]
