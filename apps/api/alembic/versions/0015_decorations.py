"""alpha decorations ownership and room equip state

Revision ID: 0015_decorations
Revises: 0014_alpha_feedback
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0015_decorations"
down_revision = "0014_alpha_feedback"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "player_decorations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("decoration_key", sa.String(80), nullable=False),
        sa.Column("purchased_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("user_id", "decoration_key", name="uq_player_decoration_user_key"),
    )
    op.create_index("ix_player_decorations_user_id", "player_decorations", ["user_id"])

    op.create_table(
        "room_decorations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("room_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False),
        sa.Column("slot_index", sa.Integer(), nullable=False),
        sa.Column("decoration_key", sa.String(80), nullable=False),
        sa.Column("equipped_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("room_id", "slot_index", name="uq_room_decoration_slot"),
        sa.UniqueConstraint("room_id", "decoration_key", name="uq_room_decoration_key"),
        sa.CheckConstraint("slot_index BETWEEN 0 AND 11", name="ck_room_decoration_slot"),
    )
    op.create_index("ix_room_decorations_room_id", "room_decorations", ["room_id"])


def downgrade():
    op.drop_index("ix_room_decorations_room_id", table_name="room_decorations")
    op.drop_table("room_decorations")
    op.drop_index("ix_player_decorations_user_id", table_name="player_decorations")
    op.drop_table("player_decorations")
