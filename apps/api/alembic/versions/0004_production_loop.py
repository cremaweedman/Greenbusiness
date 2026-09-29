"""production loop

Revision ID: 0004_production_loop
Revises: 0003_identity_bootstrap
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0004_production_loop"
down_revision = "0003_identity_bootstrap"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "crop_productions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "slot_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("production_slots.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("variety_key", sa.String(64), nullable=False),
        sa.Column("planted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ready_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("cared_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("harvested_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("yield_quantity", sa.Integer(), nullable=True),
        sa.Column("quality", sa.String(24), nullable=True),
    )
    op.create_index("ix_crop_productions_slot_id", "crop_productions", ["slot_id"])
    op.create_index("ix_crop_productions_ready_at", "crop_productions", ["ready_at"])
    op.create_index("ix_crop_productions_harvested_at", "crop_productions", ["harvested_at"])

    op.create_table(
        "inventory_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "inventory_container_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("inventory_containers.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("item_key", sa.String(96), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.UniqueConstraint(
            "inventory_container_id",
            "item_key",
            name="uq_inventory_item_container_key",
        ),
    )
    op.create_index("ix_inventory_items_container_id", "inventory_items", ["inventory_container_id"])

    op.execute(
        """
        INSERT INTO production_slots (id, room_id, slot_index, status)
        SELECT gen_random_uuid(), rooms.id, 2, 'available'
        FROM rooms
        WHERE NOT EXISTS (
            SELECT 1
            FROM production_slots
            WHERE production_slots.room_id = rooms.id
              AND production_slots.slot_index = 2
        )
        """
    )


def downgrade():
    op.drop_index("ix_inventory_items_container_id", table_name="inventory_items")
    op.drop_table("inventory_items")
    op.drop_index("ix_crop_productions_harvested_at", table_name="crop_productions")
    op.drop_index("ix_crop_productions_ready_at", table_name="crop_productions")
    op.drop_index("ix_crop_productions_slot_id", table_name="crop_productions")
    op.drop_table("crop_productions")
