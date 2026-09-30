from pathlib import Path


def test_liveops_foundation_contract_is_wired():
    api_root = Path(__file__).resolve().parents[1]
    service = (api_root / "app/liveops_service.py").read_text(encoding="utf-8")
    routes = (api_root / "app/admin_routes.py").read_text(encoding="utf-8")
    models = (api_root / "app/db/models.py").read_text(encoding="utf-8")

    assert "DEFAULT_CONFIG" in service
    assert '"production": True' in service
    assert "record_analytics_event" in service
    assert "ANALYTICS_SECRET_KEYS" in service
    assert "LiveOpsConfigVersion" in models
    assert "AnalyticsEvent" in models
    assert "/config/publish" in routes
    assert "/config/rollback" in routes
    assert "/dashboards/economy" in routes
