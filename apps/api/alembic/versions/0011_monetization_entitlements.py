"""monetization entitlements foundation

Revision ID: 0011_monetization_entitlements
Revises: 0010_social_clubs
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0011_monetization_entitlements"
down_revision = "0010_social_clubs"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "premium_wallets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("credits", sa.Integer(), nullable=False),
        sa.CheckConstraint("credits >= 0", name="ck_premium_wallets_credits_nonnegative"),
        sa.UniqueConstraint("user_id", name="uq_premium_wallets_user_id"),
    )

    op.create_table(
        "purchase_ledger",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("transaction_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("provider", sa.String(32), nullable=False),
        sa.Column("receipt_id", sa.String(128), nullable=False),
        sa.Column("product_key", sa.String(80), nullable=False),
        sa.Column("status", sa.String(24), nullable=False),
        sa.Column("premium_credits_delta", sa.Integer(), nullable=False),
        sa.Column("entitlement_keys", postgresql.JSONB(), nullable=False),
        sa.Column("receipt_hash", sa.String(64), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("refunded_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("provider", "receipt_id", name="uq_purchase_ledger_provider_receipt"),
    )
    op.create_index("ix_purchase_ledger_transaction_id", "purchase_ledger", ["transaction_id"])
    op.create_index("ix_purchase_ledger_user_id", "purchase_ledger", ["user_id"])
    op.create_index("ix_purchase_ledger_created_at", "purchase_ledger", ["created_at"])

    op.create_table(
        "player_entitlements",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("entitlement_key", sa.String(96), nullable=False),
        sa.Column(
            "source_purchase_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("purchase_ledger.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("status", sa.String(24), nullable=False),
        sa.Column(
            "granted_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("user_id", "entitlement_key", name="uq_player_entitlement_user_key"),
    )
    op.create_index("ix_player_entitlements_user_id", "player_entitlements", ["user_id"])


def downgrade():
    op.drop_index("ix_player_entitlements_user_id", table_name="player_entitlements")
    op.drop_table("player_entitlements")
    op.drop_index("ix_purchase_ledger_created_at", table_name="purchase_ledger")
    op.drop_index("ix_purchase_ledger_user_id", table_name="purchase_ledger")
    op.drop_index("ix_purchase_ledger_transaction_id", table_name="purchase_ledger")
    op.drop_table("purchase_ledger")
    op.drop_table("premium_wallets")
