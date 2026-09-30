"""skill allocations

Revision ID: 0008_skill_allocations
Revises: 0007_progression_level_curve
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0008_skill_allocations"
down_revision = "0007_progression_level_curve"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "player_skill_allocations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("skill_key", sa.String(96), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column("allocated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", "skill_key", name="uq_player_skill_user_key"),
    )
    op.create_index("ix_player_skill_allocations_user_id", "player_skill_allocations", ["user_id"])


def downgrade():
    op.drop_index("ix_player_skill_allocations_user_id", table_name="player_skill_allocations")
    op.drop_table("player_skill_allocations")
