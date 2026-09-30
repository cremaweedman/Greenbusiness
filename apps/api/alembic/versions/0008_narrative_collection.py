"""narrative and collection expansion

Revision ID: 0008_narrative_collection
Revises: 0007_missions_mastery
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0008_narrative_collection"
down_revision = "0007_missions_mastery"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "mission_pool_assignments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("period_type", sa.String(16), nullable=False),
        sa.Column("period_key", sa.String(32), nullable=False),
        sa.Column("slot_index", sa.Integer(), nullable=False),
        sa.Column("mission_key", sa.String(64), nullable=False),
        sa.Column("config_version", sa.String(32), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "user_id",
            "period_type",
            "period_key",
            "slot_index",
            name="uq_mission_pool_period_slot",
        ),
        sa.UniqueConstraint(
            "user_id",
            "period_type",
            "period_key",
            "mission_key",
            name="uq_mission_pool_period_mission",
        ),
        sa.CheckConstraint(
            "period_type IN ('daily','weekly')",
            name="ck_mission_pool_period_type",
        ),
        sa.CheckConstraint("slot_index >= 0", name="ck_mission_pool_slot_nonnegative"),
    )
    op.create_index(
        "ix_mission_pool_assignments_user_id",
        "mission_pool_assignments",
        ["user_id"],
    )
    op.create_index(
        "ix_mission_pool_assignments_period",
        "mission_pool_assignments",
        ["user_id", "period_type", "period_key"],
    )


def downgrade():
    op.drop_index("ix_mission_pool_assignments_period", table_name="mission_pool_assignments")
    op.drop_index("ix_mission_pool_assignments_user_id", table_name="mission_pool_assignments")
    op.drop_table("mission_pool_assignments")
