"""social clubs foundation

Revision ID: 0010_social_clubs
Revises: 0009_liveops_admin_analytics
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0010_social_clubs"
down_revision = "0009_liveops_admin_analytics"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "social_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("friend_code", sa.String(16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("user_id", name="uq_social_profiles_user_id"),
        sa.UniqueConstraint("friend_code", name="uq_social_profiles_friend_code"),
    )
    op.create_index("ix_social_profiles_friend_code", "social_profiles", ["friend_code"])

    op.create_table(
        "friendships",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "requester_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "addressee_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", sa.String(24), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.CheckConstraint("requester_id <> addressee_id", name="ck_friendship_not_self"),
        sa.UniqueConstraint("requester_id", "addressee_id", name="uq_friendship_pair"),
    )
    op.create_index("ix_friendships_requester_id", "friendships", ["requester_id"])
    op.create_index("ix_friendships_addressee_id", "friendships", ["addressee_id"])

    op.create_table(
        "clubs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "owner_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(48), nullable=False),
        sa.Column("slug", sa.String(64), nullable=False),
        sa.Column("invite_code", sa.String(16), nullable=False),
        sa.Column("status", sa.String(24), nullable=False),
        sa.Column("max_members", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.CheckConstraint("max_members BETWEEN 2 AND 30", name="ck_clubs_max_members"),
        sa.UniqueConstraint("slug", name="uq_clubs_slug"),
        sa.UniqueConstraint("invite_code", name="uq_clubs_invite_code"),
    )
    op.create_index("ix_clubs_owner_user_id", "clubs", ["owner_user_id"])
    op.create_index("ix_clubs_slug", "clubs", ["slug"])
    op.create_index("ix_clubs_invite_code", "clubs", ["invite_code"])

    op.create_table(
        "club_memberships",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "club_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("clubs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("role", sa.String(24), nullable=False),
        sa.Column("joined_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("user_id", name="uq_club_memberships_active_user"),
        sa.UniqueConstraint("club_id", "user_id", name="uq_club_memberships_club_user"),
    )
    op.create_index("ix_club_memberships_club_id", "club_memberships", ["club_id"])
    op.create_index("ix_club_memberships_user_id", "club_memberships", ["user_id"])

    op.create_table(
        "club_invites",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "club_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("clubs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "inviter_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "invitee_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", sa.String(24), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("responded_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("club_id", "invitee_user_id", name="uq_club_invites_club_invitee"),
    )
    op.create_index("ix_club_invites_club_id", "club_invites", ["club_id"])
    op.create_index("ix_club_invites_invitee_user_id", "club_invites", ["invitee_user_id"])

    op.create_table(
        "club_objectives",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "club_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("clubs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("period_key", sa.String(16), nullable=False),
        sa.Column("objective_key", sa.String(64), nullable=False),
        sa.Column("target_amount", sa.Integer(), nullable=False),
        sa.Column("progress_amount", sa.Integer(), nullable=False),
        sa.Column("reward_cash", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(24), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("target_amount > 0", name="ck_club_objective_target_positive"),
        sa.CheckConstraint(
            "progress_amount >= 0",
            name="ck_club_objective_progress_nonnegative",
        ),
        sa.UniqueConstraint("club_id", "period_key", name="uq_club_objectives_period"),
    )
    op.create_index("ix_club_objectives_club_id", "club_objectives", ["club_id"])

    op.create_table(
        "club_contributions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "club_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("clubs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "objective_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("club_objectives.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("event_key", sa.String(160), nullable=False),
        sa.Column("contribution_type", sa.String(32), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.CheckConstraint("amount > 0", name="ck_club_contribution_amount_positive"),
        sa.UniqueConstraint("club_id", "event_key", name="uq_club_contributions_event"),
    )
    op.create_index("ix_club_contributions_club_id", "club_contributions", ["club_id"])
    op.create_index("ix_club_contributions_objective_id", "club_contributions", ["objective_id"])
    op.create_index("ix_club_contributions_user_id", "club_contributions", ["user_id"])

    op.create_table(
        "club_assists",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "club_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("clubs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "helper_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "receiver_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("period_key", sa.String(16), nullable=False),
        sa.Column("assist_type", sa.String(32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.CheckConstraint("helper_user_id <> receiver_user_id", name="ck_club_assist_not_self"),
        sa.UniqueConstraint(
            "helper_user_id",
            "receiver_user_id",
            "period_key",
            name="uq_club_assist_helper_receiver_period",
        ),
    )
    op.create_index("ix_club_assists_club_id", "club_assists", ["club_id"])
    op.create_index("ix_club_assists_helper_user_id", "club_assists", ["helper_user_id"])
    op.create_index("ix_club_assists_receiver_user_id", "club_assists", ["receiver_user_id"])

    op.create_table(
        "club_reactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "club_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("clubs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("target_type", sa.String(32), nullable=False),
        sa.Column("target_id", sa.String(128), nullable=False),
        sa.Column("reaction_key", sa.String(24), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint(
            "club_id",
            "user_id",
            "target_type",
            "target_id",
            "reaction_key",
            name="uq_club_reaction_once",
        ),
    )
    op.create_index("ix_club_reactions_club_id", "club_reactions", ["club_id"])
    op.create_index("ix_club_reactions_user_id", "club_reactions", ["user_id"])

    op.create_table(
        "club_reward_claims",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "objective_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("club_objectives.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "club_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("clubs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("amount_cash", sa.Integer(), nullable=False),
        sa.Column("transaction_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("claimed_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("objective_id", "user_id", name="uq_club_reward_claim_objective_user"),
    )
    op.create_index("ix_club_reward_claims_objective_id", "club_reward_claims", ["objective_id"])
    op.create_index("ix_club_reward_claims_club_id", "club_reward_claims", ["club_id"])
    op.create_index("ix_club_reward_claims_user_id", "club_reward_claims", ["user_id"])


def downgrade():
    op.drop_index("ix_club_reward_claims_user_id", table_name="club_reward_claims")
    op.drop_index("ix_club_reward_claims_club_id", table_name="club_reward_claims")
    op.drop_index("ix_club_reward_claims_objective_id", table_name="club_reward_claims")
    op.drop_table("club_reward_claims")
    op.drop_index("ix_club_reactions_user_id", table_name="club_reactions")
    op.drop_index("ix_club_reactions_club_id", table_name="club_reactions")
    op.drop_table("club_reactions")
    op.drop_index("ix_club_assists_receiver_user_id", table_name="club_assists")
    op.drop_index("ix_club_assists_helper_user_id", table_name="club_assists")
    op.drop_index("ix_club_assists_club_id", table_name="club_assists")
    op.drop_table("club_assists")
    op.drop_index("ix_club_contributions_user_id", table_name="club_contributions")
    op.drop_index("ix_club_contributions_objective_id", table_name="club_contributions")
    op.drop_index("ix_club_contributions_club_id", table_name="club_contributions")
    op.drop_table("club_contributions")
    op.drop_index("ix_club_objectives_club_id", table_name="club_objectives")
    op.drop_table("club_objectives")
    op.drop_index("ix_club_invites_invitee_user_id", table_name="club_invites")
    op.drop_index("ix_club_invites_club_id", table_name="club_invites")
    op.drop_table("club_invites")
    op.drop_index("ix_club_memberships_user_id", table_name="club_memberships")
    op.drop_index("ix_club_memberships_club_id", table_name="club_memberships")
    op.drop_table("club_memberships")
    op.drop_index("ix_clubs_invite_code", table_name="clubs")
    op.drop_index("ix_clubs_slug", table_name="clubs")
    op.drop_index("ix_clubs_owner_user_id", table_name="clubs")
    op.drop_table("clubs")
    op.drop_index("ix_friendships_addressee_id", table_name="friendships")
    op.drop_index("ix_friendships_requester_id", table_name="friendships")
    op.drop_table("friendships")
    op.drop_index("ix_social_profiles_friend_code", table_name="social_profiles")
    op.drop_table("social_profiles")
