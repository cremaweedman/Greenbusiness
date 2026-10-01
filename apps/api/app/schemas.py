from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    email: str = Field(min_length=5, max_length=320)
    password: str = Field(min_length=10, max_length=128)
    display_name: str = Field(min_length=1, max_length=32)


class LoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=320)
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class LiveOpsConfigPayload(BaseModel):
    seasons: dict[str, dict[str, str]] = Field(default_factory=dict)
    featured_traits: list[str] = Field(default_factory=list)
    feature_flags: dict[str, bool] = Field(default_factory=dict)
    kill_switches: dict[str, bool] = Field(default_factory=dict)
    content_toggles: dict[str, bool] = Field(default_factory=dict)
    contract_multipliers: dict[str, float] = Field(default_factory=dict)
    event_windows: dict[str, dict[str, str]] = Field(default_factory=dict)
    notification_copy: dict[str, str] = Field(default_factory=dict)
    experiments: dict[str, list[str]] = Field(default_factory=dict)


class LiveOpsConfigResponse(BaseModel):
    version: int
    config: LiveOpsConfigPayload
    created_by: str
    restored_from_version: int | None
    created_at: datetime


class LiveOpsConfigPublishRequest(BaseModel):
    config: LiveOpsConfigPayload


class LiveOpsConfigRollbackRequest(BaseModel):
    source_version: int = Field(ge=1)


class ExperimentAssignmentResponse(BaseModel):
    config_version: int
    assignments: dict[str, str]


class AdminCashMutationRequest(BaseModel):
    user_id: uuid.UUID
    amount: int = Field(gt=0, le=100_000)
    reason: str = Field(min_length=3, max_length=160)


class AdminCashMutationResponse(BaseModel):
    user_id: uuid.UUID
    cash: int
    cash_delta: int
    transaction_id: uuid.UUID


class AdminLedgerEntryResponse(BaseModel):
    id: uuid.UUID
    transaction_id: uuid.UUID
    user_id: uuid.UUID
    currency: str
    amount: int
    source_or_sink: str
    reference_type: str
    reference_id: str
    config_version: str
    balance_before: int
    balance_after: int
    created_at: datetime


class WalletDistributionBucketResponse(BaseModel):
    label: str
    min_cash: int
    max_cash: int | None
    wallet_count: int


class AnalyticsEventResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID | None
    event_name: str
    category: str
    payload: dict[str, object]
    request_id: str | None
    created_at: datetime


class EconomyDashboardResponse(BaseModel):
    currency: str
    minted: int
    burned: int
    wallet_count: int
    total_wallet_cash: int
    min_wallet_cash: int
    max_wallet_cash: int
    wallet_distribution: list[WalletDistributionBucketResponse]


class FunnelStepResponse(BaseModel):
    event_name: str
    count: int


class CoreFunnelResponse(BaseModel):
    steps: list[FunnelStepResponse]


class CoreLoopDashboardResponse(BaseModel):
    tutorial_started: int
    tutorial_completed: int
    registered: int
    planted: int
    cared: int
    harvested: int
    contracts_accepted: int
    contracts_completed: int
    upgrades_purchased: int
    missions_completed: int
    failed_requests: int


class SocialProfileResponse(BaseModel):
    user_id: uuid.UUID
    friend_code: str
    deep_link: str


class FriendRedeemRequest(BaseModel):
    friend_code: str = Field(min_length=4, max_length=16)


class FriendResponse(BaseModel):
    user_id: uuid.UUID
    display_name: str
    friend_code: str
    since: datetime


class ClubCreateRequest(BaseModel):
    name: str = Field(min_length=3, max_length=48)


class ClubJoinRequest(BaseModel):
    invite_code: str = Field(min_length=4, max_length=16)


class ClubInviteCreateRequest(BaseModel):
    friend_code: str = Field(min_length=4, max_length=16)


class ClubContributionRequest(BaseModel):
    event_key: str = Field(min_length=6, max_length=160)
    amount: int = Field(gt=0, le=100)
    contribution_type: str = Field(default="manual", min_length=3, max_length=32)


class ClubAssistRequest(BaseModel):
    receiver_friend_code: str = Field(min_length=4, max_length=16)
    assist_type: str = Field(default="care", min_length=3, max_length=32)


class ClubReactionRequest(BaseModel):
    target_type: str = Field(min_length=3, max_length=32)
    target_id: str = Field(min_length=1, max_length=128)
    reaction_key: str = Field(min_length=2, max_length=24)


class ClubMemberResponse(BaseModel):
    user_id: uuid.UUID
    display_name: str
    role: str
    joined_at: datetime


class ClubObjectiveResponse(BaseModel):
    id: uuid.UUID
    period_key: str
    objective_key: str
    target_amount: int
    progress_amount: int
    reward_cash: int
    status: str
    completed_at: datetime | None


class ClubInviteResponse(BaseModel):
    id: uuid.UUID
    club_id: uuid.UUID
    club_name: str
    inviter_user_id: uuid.UUID
    invitee_user_id: uuid.UUID
    status: str
    created_at: datetime
    responded_at: datetime | None


class ClubContributionResponse(BaseModel):
    id: uuid.UUID
    event_key: str
    contribution_type: str
    amount: int
    objective: ClubObjectiveResponse
    idempotent: bool = False


class ClubAssistResponse(BaseModel):
    id: uuid.UUID
    helper_user_id: uuid.UUID
    receiver_user_id: uuid.UUID
    period_key: str
    assist_type: str
    remaining_weekly_assists: int


class ClubReactionResponse(BaseModel):
    id: uuid.UUID
    target_type: str
    target_id: str
    reaction_key: str
    idempotent: bool = False


class ClubRewardClaimResponse(BaseModel):
    club_id: uuid.UUID
    objective_id: uuid.UUID
    cash: int
    cash_delta: int
    transaction_id: uuid.UUID
    idempotent: bool = False


class StoreProductResponse(BaseModel):
    key: str
    title: str
    product_type: str
    price_cents: int
    currency_code: str
    premium_credits: int
    entitlement_keys: list[str]
    cosmetic_keys: list[str]
    consumable: bool
    disabled: bool = False


class StoreCatalogResponse(BaseModel):
    products: list[StoreProductResponse]
    season_pass_enabled: bool = False


class ReceiptValidationRequest(BaseModel):
    provider: str = Field(default="sandbox", min_length=3, max_length=32)
    receipt_id: str = Field(min_length=8, max_length=128)
    product_key: str = Field(min_length=3, max_length=80)


class PurchaseLedgerResponse(BaseModel):
    id: uuid.UUID
    transaction_id: uuid.UUID
    provider: str
    receipt_id: str
    product_key: str
    status: str
    premium_credits_delta: int
    entitlement_keys: list[str]
    created_at: datetime
    refunded_at: datetime | None


class EntitlementResponse(BaseModel):
    entitlement_key: str
    status: str
    granted_at: datetime
    revoked_at: datetime | None


class MonetizationStateResponse(BaseModel):
    premium_credits: int
    entitlements: list[EntitlementResponse]
    purchases: list[PurchaseLedgerResponse]


class PurchaseValidationResponse(BaseModel):
    purchase: PurchaseLedgerResponse
    premium_credits: int
    entitlements: list[EntitlementResponse]
    duplicate_receipt: bool = False


class PurchaseRefundResponse(BaseModel):
    purchase: PurchaseLedgerResponse
    premium_credits: int
    revoked_entitlement_keys: list[str]
    idempotent: bool = False


class RewardedAdClaimRequest(BaseModel):
    placement_key: str = Field(default="store_bonus", min_length=3, max_length=48)
    impression_id: str = Field(min_length=8, max_length=128)


class RewardedAdClaimResponse(BaseModel):
    placement_key: str
    reward_cash: int
    idempotent: bool = False


class ClubResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    invite_code: str
    max_members: int
    member_count: int
    user_role: str | None
    objective: ClubObjectiveResponse | None
    members: list[ClubMemberResponse]


class SocialStateResponse(BaseModel):
    profile: SocialProfileResponse
    friends: list[FriendResponse]
    club: ClubResponse | None
    pending_invites: list[ClubInviteResponse]


class AdminPlayerLookupResponse(BaseModel):
    user_id: uuid.UUID
    email: str
    status: str
    display_name: str | None
    cash: int | None
    level: int | None
    reputation: int | None
    tutorial_step: int | None
    tutorial_completed: bool | None


class StarterVarietyResponse(BaseModel):
    key: str
    name: str
    grow_seconds: int
    base_yield: int
    traits: list[str]


class CropProductionResponse(BaseModel):
    id: uuid.UUID
    variety_key: str
    variety_name: str
    planted_at: datetime
    ready_at: datetime
    cared_at: datetime | None
    is_ready: bool


class ProductionSlotResponse(BaseModel):
    id: uuid.UUID
    slot_index: int
    status: str
    crop: CropProductionResponse | None = None


class InventoryItemResponse(BaseModel):
    item_key: str
    display_name: str
    quantity: int


class InventoryLotResponse(BaseModel):
    item_key: str
    display_name: str
    quality: str
    quantity: int


class PlantRequest(BaseModel):
    variety_key: str = Field(min_length=1, max_length=64)


class HarvestResponse(BaseModel):
    slot: ProductionSlotResponse
    inventory: list[InventoryItemResponse]
    inventory_lots: list[InventoryLotResponse]
    harvested_item: InventoryItemResponse
    yield_quantity: int
    quality: str
    xp_reward: int


class ContractOfferResponse(BaseModel):
    offer_id: str
    offer_bucket: int
    key: str
    title: str
    archetype: str
    item_key: str
    item_name: str
    required_quantity: int
    required_quality: str | None
    required_trait: str | None
    reward_cash: int
    reward_reputation: int
    min_level: int
    min_reputation: int
    specialized: bool
    locked: bool
    expires_at: datetime


class PlayerContractResponse(BaseModel):
    id: uuid.UUID
    offer_id: str
    offer_bucket: int
    contract_key: str
    archetype: str
    item_key: str
    required_quantity: int
    required_quality: str | None
    required_trait: str | None
    reward_cash: int
    reward_reputation: int
    status: str
    accepted_at: datetime
    completed_at: datetime | None


class UpgradeOfferResponse(BaseModel):
    key: str
    name: str
    tier: int
    cost_cash: int
    yield_bonus: int
    min_level: int
    prerequisite_key: str | None
    locked: bool
    locked_reason: str | None


class SkillBranchResponse(BaseModel):
    branch: str
    points: int


class EconomyActionResponse(BaseModel):
    cash: int
    reputation: int
    level: int
    inventory: list[InventoryItemResponse]
    inventory_lots: list[InventoryLotResponse]
    active_contract: PlayerContractResponse | None
    active_contracts: list[PlayerContractResponse]
    owned_upgrade_keys: list[str]


class ContactResponse(BaseModel):
    key: str
    name: str
    role: str
    tone: str
    intro_message: str


class MissionRewardResponse(BaseModel):
    cash: int
    xp: int
    reputation: int


class PlayerMissionResponse(BaseModel):
    key: str
    sequence: int
    contact_key: str
    arc_key: str
    arc_title: str
    title: str
    description: str
    objective_type: str
    objective_key: str | None
    target: int
    progress: int
    status: str
    reward: MissionRewardResponse
    inbox_message: str
    completed_at: datetime | None


class VarietyMasteryResponse(BaseModel):
    variety_key: str
    variety_name: str
    harvest_quantity: int
    contract_quantity: int
    points: int
    tier: int
    next_threshold: int | None
    unlocked_cosmetic_keys: list[str]


class PlayerResponse(BaseModel):
    server_time: datetime
    user_id: uuid.UUID
    email: str
    display_name: str
    business_id: uuid.UUID
    business_name: str
    room_id: uuid.UUID
    room_slug: str
    room_level: int
    slots: list[ProductionSlotResponse]
    level: int
    xp: int
    next_level_xp: int | None
    reputation: int
    skill_points_unspent: int
    skill_branches: list[SkillBranchResponse]
    unlocked_keys: list[str]
    tutorial_step: int
    tutorial_completed: bool
    inventory_container_id: uuid.UUID
    inventory: list[InventoryItemResponse]
    inventory_lots: list[InventoryLotResponse]
    starter_varieties: list[StarterVarietyResponse]
    cash: int
    premium_credits: int
    active_entitlement_keys: list[str]
    contract_offers: list[ContractOfferResponse]
    contract_refresh_at: datetime
    active_contract: PlayerContractResponse | None
    active_contracts: list[PlayerContractResponse]
    upgrade_offers: list[UpgradeOfferResponse]
    owned_upgrade_keys: list[str]
    contacts: list[ContactResponse]
    missions: list[PlayerMissionResponse]
    daily_mission_keys: list[str]
    weekly_mission_keys: list[str]
    mastery: list[VarietyMasteryResponse]
    unlocked_cosmetic_keys: list[str]

