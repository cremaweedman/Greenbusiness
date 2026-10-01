"""closed alpha cohort membership

Revision ID: 0016_alpha_cohort
Revises: 0015_decorations
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0016_alpha_cohort"
down_revision = "0015_decorations"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "alpha_cohort_members",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("wave", sa.String(32), nullable=False, server_default="wave-1"),
        sa.Column("status", sa.String(16), nullable=False, server_default="active"),
        sa.Column("enrolled_by", sa.String(128), nullable=False),
        sa.Column(
            "enrolled_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint("user_id", name="uq_alpha_cohort_member_user"),
        sa.CheckConstraint(
            "status IN ('active','paused','completed','removed')",
            name="ck_alpha_cohort_member_status",
        ),
    )
    op.create_index("ix_alpha_cohort_members_user_id", "alpha_cohort_members", ["user_id"])
    op.create_index("ix_alpha_cohort_members_status", "alpha_cohort_members", ["status"])
    op.create_index("ix_alpha_cohort_members_enrolled_at", "alpha_cohort_members", ["enrolled_at"])


def downgrade():
    op.drop_index("ix_alpha_cohort_members_enrolled_at", table_name="alpha_cohort_members")
    op.drop_index("ix_alpha_cohort_members_status", table_name="alpha_cohort_members")
    op.drop_index("ix_alpha_cohort_members_user_id", table_name="alpha_cohort_members")
    op.drop_table("alpha_cohort_members")
