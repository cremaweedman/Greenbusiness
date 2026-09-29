"""economic loop foundation

Revision ID: 0005_economic_loop
Revises: 0004_production_loop
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0005_economic_loop"
down_revision = "0004_production_loop"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "wallets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("cash", sa.Integer(), nullable=False),
        sa.CheckConstraint("cash >= 0", name="ck_wallets_cash_nonnegative"),
        sa.UniqueConstraint("user_id", name="uq_wallets_user_id"),
    )

    op.create_table(
        "economy_ledger",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("transaction_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("currency", sa.String(24), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("source_or_sink", sa.String(64), nullable=False),
        sa.Column("reference_type", sa.String(64), nullable=False),
        sa.Column("reference_id", sa.String(128), nullable=False),
        sa.Column("config_version", sa.String(64), nullable=False),
        sa.Column("balance_before", sa.Integer(), nullable=False),
        sa.Column("balance_after", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_economy_ledger_user_id", "economy_ledger", ["user_id"])
    op.create_index("ix_economy_ledger_transaction_id", "economy_ledger", ["transaction_id"])
    op.create_index("ix_economy_ledger_created_at", "economy_ledger", ["created_at"])

    op.create_table(
        "economy_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("idempotency_key", sa.String(128), nullable=False),
        sa.Column("operation", sa.String(64), nullable=False),
        sa.Column("reference_id", sa.String(128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("user_id", "idempotency_key", name="uq_economy_requests_user_key"),
    )

    op.create_table(
        "player_contracts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("contract_key", sa.String(64), nullable=False),
        sa.Column("status", sa.String(24), nullable=False),
        sa.Column("accepted_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("user_id", "contract_key", name="uq_player_contract_user_key"),
    )
    op.create_index("ix_player_contracts_user_id", "player_contracts", ["user_id"])

    op.create_table(
        "player_upgrades",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("upgrade_key", sa.String(64), nullable=False),
        sa.Column("purchased_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("user_id", "upgrade_key", name="uq_player_upgrade_user_key"),
    )
    op.create_index("ix_player_upgrades_user_id", "player_upgrades", ["user_id"])

    op.execute(
        """
        INSERT INTO wallets (id, user_id, cash)
        SELECT gen_random_uuid(), users.id, 500
        FROM users
        WHERE NOT EXISTS (
            SELECT 1 FROM wallets WHERE wallets.user_id = users.id
        )
        """
    )

    op.execute(
        """
        INSERT INTO economy_ledger (
            id,
            transaction_id,
            user_id,
            currency,
            amount,
            source_or_sink,
            reference_type,
            reference_id,
            config_version,
            balance_before,
            balance_after
        )
        SELECT
            gen_random_uuid(),
            gen_random_uuid(),
            users.id,
            'cash',
            500,
            'bootstrap',
            'user',
            users.id::text,
            'economy_v1',
            0,
            500
        FROM users
        """
    )


def downgrade():
    op.drop_index("ix_player_upgrades_user_id", table_name="player_upgrades")
    op.drop_table("player_upgrades")
    op.drop_index("ix_player_contracts_user_id", table_name="player_contracts")
    op.drop_table("player_contracts")
    op.drop_table("economy_requests")
    op.drop_index("ix_economy_ledger_created_at", table_name="economy_ledger")
    op.drop_index("ix_economy_ledger_transaction_id", table_name="economy_ledger")
    op.drop_index("ix_economy_ledger_user_id", table_name="economy_ledger")
    op.drop_table("economy_ledger")
    op.drop_table("wallets")
