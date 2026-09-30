"""contracts and progression expansion

Revision ID: 0006_contracts_progression
Revises: 0005_economic_loop
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0006_contracts_progression"
down_revision = "0005_economic_loop"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "progression",
        sa.Column("skill_points_unspent", sa.Integer(), server_default="0", nullable=False),
    )

    op.create_table(
        "inventory_lots",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "inventory_container_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("inventory_containers.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("item_key", sa.String(96), nullable=False),
        sa.Column("quality", sa.String(24), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.CheckConstraint("quantity >= 0", name="ck_inventory_lots_quantity_nonnegative"),
        sa.UniqueConstraint(
            "inventory_container_id",
            "item_key",
            "quality",
            name="uq_inventory_lot_container_key_quality",
        ),
    )
    op.create_index(
        "ix_inventory_lots_container_id",
        "inventory_lots",
        ["inventory_container_id"],
    )

    op.execute(
        """
        INSERT INTO inventory_lots (id, inventory_container_id, item_key, quality, quantity)
        SELECT gen_random_uuid(), inventory_container_id, item_key, 'standard', quantity
        FROM inventory_items
        WHERE quantity > 0
        """
    )

    op.add_column("player_contracts", sa.Column("offer_id", sa.String(96), nullable=True))
    op.add_column("player_contracts", sa.Column("offer_bucket", sa.Integer(), nullable=True))
    op.add_column("player_contracts", sa.Column("archetype", sa.String(24), nullable=True))
    op.add_column("player_contracts", sa.Column("config_version", sa.String(64), nullable=True))
    op.add_column("player_contracts", sa.Column("item_key", sa.String(96), nullable=True))
    op.add_column("player_contracts", sa.Column("required_quantity", sa.Integer(), nullable=True))
    op.add_column("player_contracts", sa.Column("required_quality", sa.String(24), nullable=True))
    op.add_column("player_contracts", sa.Column("required_trait", sa.String(32), nullable=True))
    op.add_column("player_contracts", sa.Column("reward_cash", sa.Integer(), nullable=True))
    op.add_column("player_contracts", sa.Column("reward_reputation", sa.Integer(), nullable=True))

    op.execute(
        """
        UPDATE player_contracts
        SET
            offer_id = 'legacy:' || id::text,
            offer_bucket = 0,
            archetype = 'quick',
            config_version = 'economy_v1',
            item_key = 'starter_crop.aurora-drift',
            required_quantity = 3,
            required_quality = NULL,
            required_trait = NULL,
            reward_cash = 150,
            reward_reputation = 5
        WHERE contract_key = 'neighborhood-sampler'
        """
    )

    op.execute(
        """
        UPDATE player_contracts
        SET
            offer_id = COALESCE(offer_id, 'legacy:' || id::text),
            offer_bucket = COALESCE(offer_bucket, 0),
            archetype = COALESCE(archetype, 'standard'),
            config_version = COALESCE(config_version, 'economy_v1'),
            item_key = COALESCE(item_key, 'starter_crop.aurora-drift'),
            required_quantity = COALESCE(required_quantity, 3),
            reward_cash = COALESCE(reward_cash, 150),
            reward_reputation = COALESCE(reward_reputation, 5)
        """
    )

    op.drop_constraint("uq_player_contract_user_key", "player_contracts", type_="unique")

    for column in (
        "offer_id",
        "offer_bucket",
        "archetype",
        "config_version",
        "item_key",
        "required_quantity",
        "reward_cash",
        "reward_reputation",
    ):
        op.alter_column("player_contracts", column, nullable=False)

    op.create_unique_constraint(
        "uq_player_contract_user_offer",
        "player_contracts",
        ["user_id", "offer_id"],
    )
    op.create_index(
        "ix_player_contracts_offer_bucket",
        "player_contracts",
        ["offer_bucket"],
    )

    op.create_table(
        "player_skill_branches",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("branch", sa.String(32), nullable=False),
        sa.Column("points", sa.Integer(), nullable=False, server_default="0"),
        sa.CheckConstraint("points >= 0", name="ck_player_skill_branch_points_nonnegative"),
        sa.UniqueConstraint(
            "user_id",
            "branch",
            name="uq_player_skill_branch_user_branch",
        ),
    )
    op.create_index(
        "ix_player_skill_branches_user_id",
        "player_skill_branches",
        ["user_id"],
    )

    op.execute(
        """
        INSERT INTO player_skill_branches (id, user_id, branch, points)
        SELECT gen_random_uuid(), users.id, branches.branch, 0
        FROM users
        CROSS JOIN (
            VALUES ('botany'), ('commerce'), ('operations')
        ) AS branches(branch)
        """
    )


def downgrade():
    op.drop_index("ix_player_skill_branches_user_id", table_name="player_skill_branches")
    op.drop_table("player_skill_branches")

    op.drop_index("ix_player_contracts_offer_bucket", table_name="player_contracts")
    op.drop_constraint("uq_player_contract_user_offer", "player_contracts", type_="unique")
    op.create_unique_constraint(
        "uq_player_contract_user_key",
        "player_contracts",
        ["user_id", "contract_key"],
    )

    for column in (
        "reward_reputation",
        "reward_cash",
        "required_trait",
        "required_quality",
        "required_quantity",
        "item_key",
        "config_version",
        "archetype",
        "offer_bucket",
        "offer_id",
    ):
        op.drop_column("player_contracts", column)

    op.drop_index("ix_inventory_lots_container_id", table_name="inventory_lots")
    op.drop_table("inventory_lots")
    op.drop_column("progression", "skill_points_unspent")
