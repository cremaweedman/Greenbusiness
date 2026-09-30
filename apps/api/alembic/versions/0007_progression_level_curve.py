"""progression level curve

Revision ID: 0007_progression_level_curve
Revises: 0006_player_upgrades
"""

import sqlalchemy as sa

from alembic import op

revision = "0007_progression_level_curve"
down_revision = "0006_player_upgrades"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "progression",
        sa.Column("skill_points", sa.Integer(), server_default="0", nullable=False),
    )
    op.alter_column("progression", "skill_points", server_default=None)


def downgrade():
    op.drop_column("progression", "skill_points")
