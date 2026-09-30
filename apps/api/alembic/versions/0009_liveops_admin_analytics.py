"""liveops admin analytics foundation

Revision ID: 0009_liveops_admin_analytics
Revises: 0008_narrative_collection
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0009_liveops_admin_analytics"
down_revision = "0008_narrative_collection"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "liveops_config_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("config", postgresql.JSONB(), nullable=False),
        sa.Column("created_by", sa.String(128), nullable=False),
        sa.Column("restored_from_version", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint("version", name="uq_liveops_config_versions_version"),
    )
    op.create_index(
        "ix_liveops_config_versions_version",
        "liveops_config_versions",
        ["version"],
    )
    op.create_index(
        "ix_liveops_config_versions_created_at",
        "liveops_config_versions",
        ["created_at"],
    )

    op.create_table(
        "analytics_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("event_name", sa.String(96), nullable=False),
        sa.Column("category", sa.String(32), nullable=False),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        sa.Column("request_id", sa.String(128), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_analytics_events_user_id", "analytics_events", ["user_id"])
    op.create_index("ix_analytics_events_event_name", "analytics_events", ["event_name"])
    op.create_index("ix_analytics_events_category", "analytics_events", ["category"])
    op.create_index("ix_analytics_events_created_at", "analytics_events", ["created_at"])


def downgrade():
    op.drop_index("ix_analytics_events_created_at", table_name="analytics_events")
    op.drop_index("ix_analytics_events_category", table_name="analytics_events")
    op.drop_index("ix_analytics_events_event_name", table_name="analytics_events")
    op.drop_index("ix_analytics_events_user_id", table_name="analytics_events")
    op.drop_table("analytics_events")
    op.drop_index("ix_liveops_config_versions_created_at", table_name="liveops_config_versions")
    op.drop_index("ix_liveops_config_versions_version", table_name="liveops_config_versions")
    op.drop_table("liveops_config_versions")
