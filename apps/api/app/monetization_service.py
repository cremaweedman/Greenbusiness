from __future__ import annotations

import uuid
from datetime import UTC, datetime
from hashlib import sha256

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit import append_audit_event
from app.db.models import EconomyLedger, PlayerEntitlement, PremiumWallet, PurchaseLedger, Wallet
from app.errors import AppError
from app.game_data.store_catalog import PRODUCT_BY_KEY, PRODUCTS, STORE_CONFIG_VERSION, StoreProduct
from app.liveops_service import record_analytics_event
from app.schemas import (
    EntitlementResponse,
    MonetizationStateResponse,
    PurchaseLedgerResponse,
    PurchaseRefundResponse,
    PurchaseValidationResponse,
    RewardedAdClaimResponse,
    StoreCatalogResponse,
    StoreProductResponse,
)

REWARDED_AD_CASH = 25


def _product_response(product: StoreProduct) -> StoreProductResponse:
    return StoreProductResponse(
        key=product.key,
        title=product.title,
        product_type=product.product_type,
        price_cents=product.price_cents,
        currency_code=product.currency_code,
        premium_credits=product.premium_credits,
        entitlement_keys=list(product.entitlement_keys),
        cosmetic_keys=list(product.cosmetic_keys),
        consumable=product.consumable,
        disabled=product.disabled,
    )


def store_catalog() -> StoreCatalogResponse:
    return StoreCatalogResponse(
        products=[_product_response(product) for product in PRODUCTS],
        season_pass_enabled=False,
    )


def _receipt_hash(*, provider: str, receipt_id: str, product_key: str) -> str:
    return sha256(f"{provider}:{receipt_id}:{product_key}".encode()).hexdigest()


def _validate_sandbox_receipt(provider: str, receipt_id: str, product_key: str) -> None:
    if provider != "sandbox":
        raise AppError(
            "STORE_PROVIDER_UNSUPPORTED",
            "Only sandbox receipts are supported in this phase.",
            status_code=400,
        )
    expected_prefix = f"sandbox:{product_key}:"
    if not receipt_id.startswith(expected_prefix):
        raise AppError(
            "STORE_RECEIPT_INVALID",
            "Sandbox receipt does not match the requested product.",
            status_code=400,
        )


async def _premium_wallet_for_update(session: AsyncSession, user_id: uuid.UUID) -> PremiumWallet:
    wallet = await session.scalar(
        select(PremiumWallet).where(PremiumWallet.user_id == user_id).with_for_update()
    )
    if wallet is None:
        wallet = PremiumWallet(user_id=user_id, credits=0)
        session.add(wallet)
        await session.flush()
    return wallet


def _purchase_response(model: PurchaseLedger) -> PurchaseLedgerResponse:
    return PurchaseLedgerResponse(
        id=model.id,
        transaction_id=model.transaction_id,
        provider=model.provider,
        receipt_id=model.receipt_id,
        product_key=model.product_key,
        status=model.status,
        premium_credits_delta=model.premium_credits_delta,
        entitlement_keys=list(model.entitlement_keys),
        created_at=model.created_at,
        refunded_at=model.refunded_at,
    )


def _entitlement_response(model: PlayerEntitlement) -> EntitlementResponse:
    return EntitlementResponse(
        entitlement_key=model.entitlement_key,
        status=model.status,
        granted_at=model.granted_at,
        revoked_at=model.revoked_at,
    )


async def _state_parts(
    session: AsyncSession,
    user_id: uuid.UUID,
) -> tuple[int, list[EntitlementResponse], list[PurchaseLedgerResponse]]:
    wallet = await session.scalar(select(PremiumWallet).where(PremiumWallet.user_id == user_id))
    entitlements = (
        await session.scalars(
            select(PlayerEntitlement)
            .where(PlayerEntitlement.user_id == user_id)
            .order_by(PlayerEntitlement.granted_at, PlayerEntitlement.entitlement_key)
        )
    ).all()
    purchases = (
        await session.scalars(
            select(PurchaseLedger)
            .where(PurchaseLedger.user_id == user_id)
            .order_by(PurchaseLedger.created_at.desc(), PurchaseLedger.id)
        )
    ).all()
    return (
        wallet.credits if wallet else 0,
        [_entitlement_response(item) for item in entitlements],
        [_purchase_response(item) for item in purchases],
    )


async def monetization_state(session: AsyncSession, user_id: uuid.UUID) -> MonetizationStateResponse:
    credits, entitlements, purchases = await _state_parts(session, user_id)
    return MonetizationStateResponse(
        premium_credits=credits,
        entitlements=entitlements,
        purchases=purchases,
    )


async def validate_purchase_receipt(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    provider: str,
    receipt_id: str,
    product_key: str,
    request_id: str | None = None,
) -> PurchaseValidationResponse:
    provider = provider.lower().strip()
    product = PRODUCT_BY_KEY.get(product_key)
    if product is None or product.disabled:
        raise AppError("STORE_PRODUCT_NOT_FOUND", "Store product was not found.", status_code=404)
    _validate_sandbox_receipt(provider, receipt_id, product_key)

    existing = await session.scalar(
        select(PurchaseLedger).where(
            PurchaseLedger.provider == provider,
            PurchaseLedger.receipt_id == receipt_id,
        )
    )
    if existing is not None:
        if existing.user_id != user_id:
            raise AppError(
                "STORE_RECEIPT_REPLAYED",
                "Receipt has already been claimed by another player.",
                status_code=409,
            )
        credits, entitlements, _purchases = await _state_parts(session, user_id)
        return PurchaseValidationResponse(
            purchase=_purchase_response(existing),
            premium_credits=credits,
            entitlements=entitlements,
            duplicate_receipt=True,
        )

    wallet = await _premium_wallet_for_update(session, user_id)
    before_credits = wallet.credits
    wallet.credits += product.premium_credits
    purchase = PurchaseLedger(
        transaction_id=uuid.uuid4(),
        user_id=user_id,
        provider=provider,
        receipt_id=receipt_id,
        product_key=product.key,
        status="granted",
        premium_credits_delta=product.premium_credits,
        entitlement_keys=list(product.entitlement_keys),
        receipt_hash=_receipt_hash(
            provider=provider,
            receipt_id=receipt_id,
            product_key=product.key,
        ),
    )
    session.add(purchase)
    await session.flush()

    for entitlement_key in product.entitlement_keys:
        entitlement = await session.scalar(
            select(PlayerEntitlement).where(
                PlayerEntitlement.user_id == user_id,
                PlayerEntitlement.entitlement_key == entitlement_key,
            )
        )
        if entitlement is None:
            session.add(
                PlayerEntitlement(
                    user_id=user_id,
                    entitlement_key=entitlement_key,
                    source_purchase_id=purchase.id,
                    status="active",
                )
            )
        else:
            entitlement.status = "active"
            entitlement.revoked_at = None
            entitlement.source_purchase_id = purchase.id

    await append_audit_event(
        session,
        event_type="store.purchase_granted",
        actor_type="user",
        actor_id=str(user_id),
        target_type="purchase",
        target_id=str(purchase.id),
        request_id=request_id,
        payload={
            "product_key": product.key,
            "premium_credits_delta": product.premium_credits,
            "entitlement_keys": list(product.entitlement_keys),
        },
    )
    await record_analytics_event(
        session,
        event_name="store.purchase_granted",
        user_id=user_id,
        request_id=request_id,
        payload={
            "product_key": product.key,
            "premium_credits_delta": product.premium_credits,
            "balance_before": before_credits,
            "balance_after": wallet.credits,
        },
    )
    await session.commit()

    credits, entitlements, _purchases = await _state_parts(session, user_id)
    return PurchaseValidationResponse(
        purchase=_purchase_response(purchase),
        premium_credits=credits,
        entitlements=entitlements,
    )


async def refund_purchase(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    purchase_id: uuid.UUID,
    request_id: str | None = None,
) -> PurchaseRefundResponse:
    purchase = await session.scalar(
        select(PurchaseLedger)
        .where(PurchaseLedger.id == purchase_id, PurchaseLedger.user_id == user_id)
        .with_for_update()
    )
    if purchase is None:
        raise AppError("STORE_PURCHASE_NOT_FOUND", "Purchase was not found.", status_code=404)
    wallet = await _premium_wallet_for_update(session, user_id)
    if purchase.status == "refunded":
        return PurchaseRefundResponse(
            purchase=_purchase_response(purchase),
            premium_credits=wallet.credits,
            revoked_entitlement_keys=[],
            idempotent=True,
        )

    credit_reversal = purchase.premium_credits_delta
    if credit_reversal > wallet.credits:
        raise AppError(
            "STORE_REFUND_CREDIT_SPENT",
            "Cannot refund because premium credits from this purchase were already spent.",
            status_code=409,
            details={"available_credits": wallet.credits, "required_reversal": credit_reversal},
        )
    wallet.credits -= credit_reversal
    purchase.status = "refunded"
    purchase.refunded_at = datetime.now(UTC)

    revoked: list[str] = []
    for entitlement_key in purchase.entitlement_keys:
        entitlement = await session.scalar(
            select(PlayerEntitlement).where(
                PlayerEntitlement.user_id == user_id,
                PlayerEntitlement.entitlement_key == entitlement_key,
            )
        )
        if entitlement is not None and entitlement.status == "active":
            entitlement.status = "revoked"
            entitlement.revoked_at = datetime.now(UTC)
            revoked.append(entitlement_key)

    await append_audit_event(
        session,
        event_type="store.purchase_refunded",
        actor_type="user",
        actor_id=str(user_id),
        target_type="purchase",
        target_id=str(purchase.id),
        request_id=request_id,
        payload={"revoked_entitlement_keys": revoked, "premium_credits_delta": -credit_reversal},
    )
    await record_analytics_event(
        session,
        event_name="store.purchase_refunded",
        user_id=user_id,
        request_id=request_id,
        payload={"product_key": purchase.product_key, "premium_credits_delta": -credit_reversal},
    )
    await session.commit()
    return PurchaseRefundResponse(
        purchase=_purchase_response(purchase),
        premium_credits=wallet.credits,
        revoked_entitlement_keys=revoked,
    )


async def claim_rewarded_ad(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    placement_key: str,
    impression_id: str,
    request_id: str | None = None,
) -> RewardedAdClaimResponse:
    reference_id = f"rewarded_ad:{placement_key}:{impression_id}"
    existing = await session.scalar(
        select(EconomyLedger).where(
            EconomyLedger.user_id == user_id,
            EconomyLedger.reference_type == "rewarded_ad",
            EconomyLedger.reference_id == reference_id,
        )
    )
    if existing is not None:
        return RewardedAdClaimResponse(
            placement_key=placement_key,
            reward_cash=0,
            idempotent=True,
        )
    wallet = await session.scalar(select(Wallet).where(Wallet.user_id == user_id).with_for_update())
    if wallet is None:
        raise AppError("PLAYER_STATE_INCOMPLETE", "Player wallet is missing.", status_code=500)
    before = wallet.cash
    wallet.cash += REWARDED_AD_CASH
    session.add(
        EconomyLedger(
            transaction_id=uuid.uuid4(),
            user_id=user_id,
            currency="cash",
            amount=REWARDED_AD_CASH,
            source_or_sink="rewarded_ad",
            reference_type="rewarded_ad",
            reference_id=reference_id,
            config_version=STORE_CONFIG_VERSION,
            balance_before=before,
            balance_after=wallet.cash,
        )
    )
    await record_analytics_event(
        session,
        event_name="store.rewarded_ad_claimed",
        user_id=user_id,
        request_id=request_id,
        payload={"placement_key": placement_key, "cash_delta": REWARDED_AD_CASH},
    )
    await session.commit()
    return RewardedAdClaimResponse(placement_key=placement_key, reward_cash=REWARDED_AD_CASH)
