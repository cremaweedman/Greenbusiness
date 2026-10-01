"""notifications accessibility foundation

Revision ID: 0012_notifications_accessibility
Revises: 0011_monetization_entitlements
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0012_notifications_accessibility"
down_revision = "0011_monetization_entitlements"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "notification_preferences",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("production_enabled", sa.Boolean(), nullable=False),
        sa.Column("events_enabled", sa.Boolean(), nullable=False),
        sa.Column("social_enabled", sa.Boolean(), nullable=False),
        sa.Column("quiet_hours_enabled", sa.Boolean(), nullable=False),
        sa.Column("quiet_hours_start", sa.String(5), nullable=False),
        sa.Column("quiet_hours_end", sa.String(5), nullable=False),
        sa.Column("timezone", sa.String(64), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("user_id", name="uq_notification_preferences_user_id"),
    )

    op.create_table(
        "push_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("platform", sa.String(24), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False),
        sa.Column("token_label", sa.String(32), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("user_id", "token_hash", name="uq_push_token_user_hash"),
    )
    op.create_index("ix_push_tokens_user_id", "push_tokens", ["user_id"])
    op.create_index("ix_push_tokens_token_hash", "push_tokens", ["token_hash"])


def downgrade():
    op.drop_index("ix_push_tokens_token_hash", table_name="push_tokens")
    op.drop_index("ix_push_tokens_user_id", table_name="push_tokens")
    op.drop_table("push_tokens")
    op.drop_table("notification_preferences")
