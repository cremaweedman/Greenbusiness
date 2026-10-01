from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user_id, get_db
from app.monetization_service import (
    claim_rewarded_ad,
    monetization_state,
    refund_purchase,
    store_catalog,
    validate_purchase_receipt,
)
from app.schemas import (
    MonetizationStateResponse,
    PurchaseRefundResponse,
    PurchaseValidationResponse,
    ReceiptValidationRequest,
    RewardedAdClaimRequest,
    RewardedAdClaimResponse,
    StoreCatalogResponse,
)

store_router = APIRouter(prefix="/store", tags=["store"])

DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUserId = Annotated[uuid.UUID, Depends(get_current_user_id)]


@store_router.get("/catalog", response_model=StoreCatalogResponse)
async def catalog() -> StoreCatalogResponse:
    return store_catalog()


@store_router.get("/me", response_model=MonetizationStateResponse)
async def get_store_state(
    user_id: CurrentUserId,
    session: DbSession,
) -> MonetizationStateResponse:
    return await monetization_state(session, user_id)


@store_router.post("/purchases/validate", response_model=PurchaseValidationResponse)
async def validate_purchase(
    body: ReceiptValidationRequest,
    request: Request,
    user_id: CurrentUserId,
    session: DbSession,
) -> PurchaseValidationResponse:
    return await validate_purchase_receipt(
        session,
        user_id=user_id,
        provider=body.provider,
        receipt_id=body.receipt_id,
        product_key=body.product_key,
        request_id=getattr(request.state, "request_id", None),
    )


@store_router.post("/purchases/{purchase_id}/refund", response_model=PurchaseRefundResponse)
async def refund(
    purchase_id: uuid.UUID,
    request: Request,
    user_id: CurrentUserId,
    session: DbSession,
) -> PurchaseRefundResponse:
    return await refund_purchase(
        session,
        user_id=user_id,
        purchase_id=purchase_id,
        request_id=getattr(request.state, "request_id", None),
    )


@store_router.post("/rewarded-ads/claim", response_model=RewardedAdClaimResponse)
async def rewarded_ad_claim(
    body: RewardedAdClaimRequest,
    request: Request,
    user_id: CurrentUserId,
    session: DbSession,
) -> RewardedAdClaimResponse:
    return await claim_rewarded_ad(
        session,
        user_id=user_id,
        placement_key=body.placement_key,
        impression_id=body.impression_id,
        request_id=getattr(request.state, "request_id", None),
    )
