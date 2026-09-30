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


class StarterVarietyResponse(BaseModel):
    key: str
    name: str
    grow_seconds: int
    base_yield: int


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


class ContractRequirementResponse(BaseModel):
    item_key: str
    display_name: str
    quantity: int
    quality_required: str | None = None


class ContractResponse(BaseModel):
    key: str
    name: str
    tier: str
    description: str
    requirement: ContractRequirementResponse
    cash_reward: int
    can_complete: bool
    completed: bool


class PlantRequest(BaseModel):
    variety_key: str = Field(min_length=1, max_length=64)


class HarvestResponse(BaseModel):
    slot: ProductionSlotResponse
    inventory: list[InventoryItemResponse]
    harvested_item: InventoryItemResponse
    yield_quantity: int
    quality: str
    xp_reward: int


class ContractCompletionResponse(BaseModel):
    contract: ContractResponse
    inventory: list[InventoryItemResponse]
    cash_balance: int
    cash_delta: int


class CurrencyLedgerEntryResponse(BaseModel):
    id: uuid.UUID
    currency: str
    source: str
    source_id: str
    amount: int
    balance_before: int
    balance_after: int
    config_version: str
    created_at: datetime


class EconomySummaryResponse(BaseModel):
    currency: str
    balance: int
    minted: int
    burned: int
    entry_count: int
    config_versions: list[str]


class UpgradeEffectsResponse(BaseModel):
    yield_bonus: int


class UpgradeResponse(BaseModel):
    key: str
    name: str
    description: str
    cash_cost: int
    level: int
    max_level: int
    effects: UpgradeEffectsResponse
    can_purchase: bool


class UpgradePurchaseResponse(BaseModel):
    upgrade: UpgradeResponse
    cash_balance: int
    cash_delta: int
    economy_summary: EconomySummaryResponse


class ProgressionResponse(BaseModel):
    level: int
    xp: int
    reputation: int
    skill_points: int
    max_level: int
    current_level_xp: int
    next_level_xp: int | None
    next_unlock: str | None


class SkillEffectsResponse(BaseModel):
    care_yield_bonus: int
    contract_cash_bonus: int
    grow_seconds_reduction: int


class SkillNodeResponse(BaseModel):
    key: str
    branch: str
    name: str
    description: str
    rank: int
    max_rank: int
    cost_per_rank: int
    can_allocate: bool
    effects: SkillEffectsResponse


class SkillAllocationResponse(BaseModel):
    skill: SkillNodeResponse
    progression: ProgressionResponse
    skills: list[SkillNodeResponse]


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
    reputation: int
    skill_points: int
    progression: ProgressionResponse
    cash_balance: int
    tutorial_step: int
    tutorial_completed: bool
    inventory_container_id: uuid.UUID
    inventory: list[InventoryItemResponse]
    starter_varieties: list[StarterVarietyResponse]
    contracts: list[ContractResponse]
    cash_ledger: list[CurrencyLedgerEntryResponse]
    economy_summary: EconomySummaryResponse
    upgrades: list[UpgradeResponse]
    skills: list[SkillNodeResponse]
