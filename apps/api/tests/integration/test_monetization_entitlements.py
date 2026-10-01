from __future__ import annotations

import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.config import settings
from app.db.models import PlayerEntitlement, PremiumWallet, PurchaseLedger, User, Wallet
from app.db.session import SessionLocal
from app.main import app


@pytest.fixture(autouse=True)
def sandbox_runtime(monkeypatch):
    monkeypatch.setattr(settings, "app_env", "test")
    monkeypatch.setattr(settings, "sandbox_monetization_enabled", True)
    monkeypatch.setattr(settings, "sandbox_rewarded_ads_enabled", True)


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as value:
        yield value


async def _cleanup(*emails: str) -> None:
    async with SessionLocal() as session:
        for email in emails:
            user = await session.scalar(select(User).where(User.email == email))
            if user is not None:
                await session.delete(user)
        await session.commit()


async def _register(client: AsyncClient, email: str) -> str:
    response = await client.post(
        "/v1/auth/register",
        json={
            "email": email,
            "password": "A-strong-password-753",
            "display_name": "Buyer",
        },
    )
    assert response.status_code == 201
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_store_receipts_entitlements_refunds_and_rewarded_ads_are_safe(
    client: AsyncClient,
):
    buyer_email = f"p7-buyer-{uuid.uuid4()}@example.com"
    other_email = f"p7-other-{uuid.uuid4()}@example.com"
    try:
        buyer_token = await _register(client, buyer_email)
        other_token = await _register(client, other_email)
        buyer = {"Authorization": f"Bearer {buyer_token}"}
        other = {"Authorization": f"Bearer {other_token}"}

        catalog = await client.get("/v1/store/catalog")
        assert catalog.status_code == 200
        products = {item["key"]: item for item in catalog.json()["products"]}
        assert "starter-cosmetic-bundle" in products
        assert products["starter-cosmetic-bundle"]["premium_credits"] == 0
        assert products["credits-small"]["premium_credits"] == 120
        assert catalog.json()["season_pass_enabled"] is False

        invalid = await client.post(
            "/v1/store/purchases/validate",
            headers=buyer,
            json={
                "provider": "sandbox",
                "receipt_id": "sandbox:credits-small:wrong-product",
                "product_key": "credits-medium",
            },
        )
        assert invalid.status_code == 400
        assert invalid.json()["error"]["code"] == "STORE_RECEIPT_INVALID"

        purchase = await client.post(
            "/v1/store/purchases/validate",
            headers=buyer,
            json={
                "provider": "sandbox",
                "receipt_id": "sandbox:credits-small:first",
                "product_key": "credits-small",
            },
        )
        assert purchase.status_code == 200
        purchase_body = purchase.json()
        assert purchase_body["premium_credits"] == 120
        assert purchase_body["purchase"]["premium_credits_delta"] == 120
        purchase_id = purchase_body["purchase"]["id"]

        replay = await client.post(
            "/v1/store/purchases/validate",
            headers=buyer,
            json={
                "provider": "sandbox",
                "receipt_id": "sandbox:credits-small:first",
                "product_key": "credits-small",
            },
        )
        assert replay.status_code == 200
        assert replay.json()["duplicate_receipt"] is True
        assert replay.json()["premium_credits"] == 120

        stolen = await client.post(
            "/v1/store/purchases/validate",
            headers=other,
            json={
                "provider": "sandbox",
                "receipt_id": "sandbox:credits-small:first",
                "product_key": "credits-small",
            },
        )
        assert stolen.status_code == 409
        assert stolen.json()["error"]["code"] == "STORE_RECEIPT_REPLAYED"

        founder = await client.post(
            "/v1/store/purchases/validate",
            headers=buyer,
            json={
                "provider": "sandbox",
                "receipt_id": "sandbox:founder-supporter-pack:first",
                "product_key": "founder-supporter-pack",
            },
        )
        assert founder.status_code == 200
        assert founder.json()["premium_credits"] == 620
        entitlement_keys = {
            item["entitlement_key"]
            for item in founder.json()["entitlements"]
            if item["status"] == "active"
        }
        assert "entitlement.founder_badge" in entitlement_keys
        assert "entitlement.no_ads" in entitlement_keys
        founder_purchase_id = founder.json()["purchase"]["id"]

        refund = await client.post(f"/v1/store/purchases/{founder_purchase_id}/refund", headers=buyer)
        assert refund.status_code == 200
        assert refund.json()["premium_credits"] == 120
        assert "entitlement.founder_badge" in refund.json()["revoked_entitlement_keys"]

        refund_replay = await client.post(
            f"/v1/store/purchases/{founder_purchase_id}/refund",
            headers=buyer,
        )
        assert refund_replay.status_code == 200
        assert refund_replay.json()["idempotent"] is True

        credits_refund = await client.post(f"/v1/store/purchases/{purchase_id}/refund", headers=buyer)
        assert credits_refund.status_code == 200
        assert credits_refund.json()["premium_credits"] == 0

        ad = await client.post(
            "/v1/store/rewarded-ads/claim",
            headers=buyer,
            json={"placement_key": "store_bonus", "impression_id": "impression-one"},
        )
        assert ad.status_code == 200
        assert ad.json()["reward_cash"] == 25
        ad_replay = await client.post(
            "/v1/store/rewarded-ads/claim",
            headers=buyer,
            json={"placement_key": "store_bonus", "impression_id": "impression-one"},
        )
        assert ad_replay.status_code == 200
        assert ad_replay.json()["idempotent"] is True

        async with SessionLocal() as session:
            buyer_model = await session.scalar(select(User).where(User.email == buyer_email))
            assert buyer_model is not None
            wallet = await session.scalar(select(PremiumWallet).where(PremiumWallet.user_id == buyer_model.id))
            assert wallet is not None
            assert wallet.credits == 0
            purchases = (
                await session.scalars(
                    select(PurchaseLedger).where(PurchaseLedger.user_id == buyer_model.id)
                )
            ).all()
            assert {item.status for item in purchases} == {"refunded"}
            entitlement = await session.scalar(
                select(PlayerEntitlement).where(
                    PlayerEntitlement.user_id == buyer_model.id,
                    PlayerEntitlement.entitlement_key == "entitlement.founder_badge",
                )
            )
            assert entitlement is not None
            assert entitlement.status == "revoked"
            cash_wallet = await session.scalar(select(Wallet).where(Wallet.user_id == buyer_model.id))
            assert cash_wallet is not None
            assert cash_wallet.cash == 525
    finally:
        await _cleanup(buyer_email, other_email)


@pytest.mark.asyncio
async def test_sandbox_store_is_hidden_when_disabled(client: AsyncClient, monkeypatch):
    email = f"p9-disabled-{uuid.uuid4()}@example.com"
    try:
        token = await _register(client, email)
        headers = {"Authorization": f"Bearer {token}"}
        monkeypatch.setattr(settings, "sandbox_monetization_enabled", False)
        monkeypatch.setattr(settings, "sandbox_rewarded_ads_enabled", False)

        purchase = await client.post(
            "/v1/store/purchases/validate",
            headers=headers,
            json={
                "provider": "sandbox",
                "receipt_id": "sandbox:credits-small:blocked",
                "product_key": "credits-small",
            },
        )
        assert purchase.status_code == 404
        assert purchase.json()["error"]["code"] == "STORE_SANDBOX_DISABLED"

        ad = await client.post(
            "/v1/store/rewarded-ads/claim",
            headers=headers,
            json={"placement_key": "store_bonus", "impression_id": "blocked-impression"},
        )
        assert ad.status_code == 404
        assert ad.json()["error"]["code"] == "REWARDED_ADS_DISABLED"
    finally:
        await _cleanup(email)
