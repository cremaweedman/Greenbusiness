"""contracts and cash ledger

Revision ID: 0005_contracts_economy
Revises: 0004_production_loop
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0005_contracts_economy"
down_revision = "0004_production_loop"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "currency_ledger_entries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("currency", sa.String(24), nullable=False),
        sa.Column("source", sa.String(64), nullable=False),
        sa.Column("source_id", sa.String(128), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("balance_before", sa.Integer(), nullable=False),
        sa.Column("balance_after", sa.Integer(), nullable=False),
        sa.Column("config_version", sa.String(32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint(
            "user_id",
            "currency",
            "source",
            "source_id",
            name="uq_currency_ledger_user_source",
        ),
    )
    op.create_index("ix_currency_ledger_entries_user_id", "currency_ledger_entries", ["user_id"])

    op.create_table(
        "contract_completions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("contract_key", sa.String(96), nullable=False),
        sa.Column("item_key", sa.String(96), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("quality_required", sa.String(24), nullable=True),
        sa.Column("cash_reward", sa.Integer(), nullable=False),
        sa.Column("config_version", sa.String(32), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", "contract_key", name="uq_contract_completion_user_contract"),
    )
    op.create_index("ix_contract_completions_user_id", "contract_completions", ["user_id"])


def downgrade():
    op.drop_index("ix_contract_completions_user_id", table_name="contract_completions")
    op.drop_table("contract_completions")
    op.drop_index("ix_currency_ledger_entries_user_id", table_name="currency_ledger_entries")
    op.drop_table("currency_ledger_entries")
