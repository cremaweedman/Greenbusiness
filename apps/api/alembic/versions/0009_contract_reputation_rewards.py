"""contract reputation rewards

Revision ID: 0009_contract_reputation_rewards
Revises: 0008_skill_allocations
"""

import sqlalchemy as sa

from alembic import op

revision = "0009_contract_reputation_rewards"
down_revision = "0008_skill_allocations"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "contract_completions",
        sa.Column("reputation_reward", sa.Integer(), server_default="0", nullable=False),
    )
    op.alter_column("contract_completions", "reputation_reward", server_default=None)


def downgrade():
    op.drop_column("contract_completions", "reputation_reward")
