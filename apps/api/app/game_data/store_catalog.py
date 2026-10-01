from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StoreProduct:
    key: str
    title: str
    product_type: str
    price_cents: int
    currency_code: str
    premium_credits: int
    entitlement_keys: tuple[str, ...] = ()
    cosmetic_keys: tuple[str, ...] = ()
    consumable: bool = False
    disabled: bool = False


STORE_CONFIG_VERSION = "store_v1"

PRODUCTS: tuple[StoreProduct, ...] = (
    StoreProduct(
        key="starter-cosmetic-bundle",
        title="Starter Cosmetic Bundle",
        product_type="cosmetic_bundle",
        price_cents=499,
        currency_code="USD",
        premium_credits=0,
        entitlement_keys=("cosmetic.room.starter_wall", "cosmetic.badge.early_grower"),
        cosmetic_keys=("starter_wall", "early_grower_badge"),
    ),
    StoreProduct(
        key="credits-small",
        title="Credits S",
        product_type="premium_currency",
        price_cents=199,
        currency_code="USD",
        premium_credits=120,
        consumable=True,
    ),
    StoreProduct(
        key="credits-medium",
        title="Credits M",
        product_type="premium_currency",
        price_cents=499,
        currency_code="USD",
        premium_credits=325,
        consumable=True,
    ),
    StoreProduct(
        key="credits-large",
        title="Credits L",
        product_type="premium_currency",
        price_cents=999,
        currency_code="USD",
        premium_credits=700,
        consumable=True,
    ),
    StoreProduct(
        key="founder-supporter-pack",
        title="Founder/Supporter Pack",
        product_type="supporter_pack",
        price_cents=1499,
        currency_code="USD",
        premium_credits=500,
        entitlement_keys=(
            "entitlement.founder_badge",
            "entitlement.supporter_room_plate",
            "entitlement.no_ads",
        ),
        cosmetic_keys=("founder_badge", "supporter_room_plate"),
    ),
)

PRODUCT_BY_KEY = {product.key: product for product in PRODUCTS}
