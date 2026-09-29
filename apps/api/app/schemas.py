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


class PlantRequest(BaseModel):
    variety_key: str = Field(min_length=1, max_length=64)


class HarvestResponse(BaseModel):
    slot: ProductionSlotResponse
    inventory: list[InventoryItemResponse]
    harvested_item: InventoryItemResponse
    yield_quantity: int
    quality: str


class PlayerResponse(BaseModel):
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
    inventory_container_id: uuid.UUID
    inventory: list[InventoryItemResponse]
    starter_varieties: list[StarterVarietyResponse]
