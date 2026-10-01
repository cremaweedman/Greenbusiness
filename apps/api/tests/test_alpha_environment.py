from app.config import PRODUCTION_ENVS


def test_alpha_is_production_like_for_fail_closed_security():
    assert "alpha" in PRODUCTION_ENVS
