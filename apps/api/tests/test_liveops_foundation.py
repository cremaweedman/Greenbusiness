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
    assert "admin_cash_mutation" in service
    assert "contract_reward_multipliers" in service
    assert "experiment_assignments" in service
    assert "wallet_distribution" in service
    assert "core_loop_dashboard" in service
    assert "errors.api_request_failed" in service
    assert "LiveOpsConfigVersion" in models
    assert "AnalyticsEvent" in models
    assert "/config/publish" in routes
    assert "/config/rollback" in routes
    assert "/config/versions" in routes
    assert "/experiments" in routes
    assert "/ledger" in routes
    assert "/cash/grant" in routes
    assert "/cash/revoke" in routes
    assert "/dashboards/economy" in routes
    assert "/dashboards/core-loop" in routes
