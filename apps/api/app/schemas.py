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
    contacts: list[ContactResponse]
    missions: list[PlayerMissionResponse]
    daily_mission_keys: list[str]
    weekly_mission_keys: list[str]
    mastery: list[VarietyMasteryResponse]
    unlocked_cosmetic_keys: list[str]


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
    title: str
    description: str
    objective_type: str
    objective_key: str | None
    target: int
    progress: int
    status: str
    reward: MissionRewardResponse
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
    contract_offers: list[ContractOfferResponse]
    contract_refresh_at: datetime
    active_contract: PlayerContractResponse | None
    active_contracts: list[PlayerContractResponse]
    upgrade_offers: list[UpgradeOfferResponse]
    owned_upgrade_keys: list[str]

