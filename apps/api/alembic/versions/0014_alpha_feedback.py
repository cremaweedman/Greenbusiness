"""closed alpha feedback and cohort instrumentation

Revision ID: 0014_alpha_feedback
Revises: 0013_p9_hardening
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0014_alpha_feedback"
down_revision = "0013_p9_hardening"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "alpha_feedback",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("kind", sa.String(16), nullable=False),
        sa.Column("severity", sa.String(16), nullable=False),
        sa.Column("category", sa.String(48), nullable=False),
        sa.Column("message", sa.String(2000), nullable=False),
        sa.Column("build_sha", sa.String(64)),
        sa.Column("liveops_version", sa.Integer()),
        sa.Column("status", sa.String(16), nullable=False, server_default="new"),
        sa.Column("triaged_by", sa.String(128)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("kind IN ('bug','feedback')", name="ck_alpha_feedback_kind"),
        sa.CheckConstraint(
            "severity IN ('blocker','major','minor','suggestion')",
            name="ck_alpha_feedback_severity",
        ),
        sa.CheckConstraint(
            "status IN ('new','triaged','resolved','wont_fix')",
            name="ck_alpha_feedback_status",
        ),
    )
    op.create_index("ix_alpha_feedback_user_id", "alpha_feedback", ["user_id"])
    op.create_index("ix_alpha_feedback_status", "alpha_feedback", ["status"])
    op.create_index("ix_alpha_feedback_created_at", "alpha_feedback", ["created_at"])


def downgrade():
    op.drop_index("ix_alpha_feedback_created_at", table_name="alpha_feedback")
    op.drop_index("ix_alpha_feedback_status", table_name="alpha_feedback")
    op.drop_index("ix_alpha_feedback_user_id", table_name="alpha_feedback")
    op.drop_table("alpha_feedback")
