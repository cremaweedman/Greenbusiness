"""mission engine and mastery slice

Revision ID: 0007_missions_mastery
Revises: 0006_contracts_progression
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0007_missions_mastery"
down_revision = "0006_contracts_progression"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "player_missions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mission_key", sa.String(64), nullable=False),
        sa.Column("status", sa.String(24), nullable=False),
        sa.Column("progress", sa.Integer(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rewarded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("user_id", "mission_key", name="uq_player_mission_user_key"),
        sa.CheckConstraint("progress >= 0", name="ck_player_missions_progress_nonnegative"),
    )
    op.create_index("ix_player_missions_user_id", "player_missions", ["user_id"])

    op.create_table(
        "mission_event_receipts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_key", sa.String(160), nullable=False),
        sa.Column("event_type", sa.String(48), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("user_id", "event_key", name="uq_mission_event_user_key"),
    )
    op.create_index("ix_mission_event_receipts_user_id", "mission_event_receipts", ["user_id"])

    op.create_table(
        "player_variety_mastery",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("variety_key", sa.String(64), nullable=False),
        sa.Column("harvest_quantity", sa.Integer(), nullable=False),
        sa.Column("contract_quantity", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("user_id", "variety_key", name="uq_variety_mastery_user_variety"),
        sa.CheckConstraint("harvest_quantity >= 0", name="ck_mastery_harvest_nonnegative"),
        sa.CheckConstraint("contract_quantity >= 0", name="ck_mastery_contract_nonnegative"),
    )
    op.create_index("ix_player_variety_mastery_user_id", "player_variety_mastery", ["user_id"])


def downgrade():
    op.drop_index("ix_player_variety_mastery_user_id", table_name="player_variety_mastery")
    op.drop_table("player_variety_mastery")
    op.drop_index("ix_mission_event_receipts_user_id", table_name="mission_event_receipts")
    op.drop_table("mission_event_receipts")
    op.drop_index("ix_player_missions_user_id", table_name="player_missions")
    op.drop_table("player_missions")
