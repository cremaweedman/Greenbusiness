"""P9 hardening

Revision ID: 0013_p9_hardening
Revises: 0012_notifications_accessibility
"""

from alembic import op
import sqlalchemy as sa

revision = "0013_p9_hardening"
down_revision = "0012_notifications_accessibility"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("push_tokens", sa.Column("token_ciphertext", sa.String(1024), nullable=True))


def downgrade():
    op.drop_column("push_tokens", "token_ciphertext")
