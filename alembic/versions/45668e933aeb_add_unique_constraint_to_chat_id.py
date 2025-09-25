"""add_unique_constraint_to_chat_id

Revision ID: 45668e933aeb
Revises: d4e6357d2aa2
Create Date: 2025-09-24 19:19:52.005961

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "45668e933aeb"
down_revision: str | Sequence[str] | None = "d4e6357d2aa2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Remove duplicate chat_id entries, keeping only the first one
    op.execute("""
        DELETE FROM notification_subscriptions
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM notification_subscriptions
            GROUP BY chat_id
        )
    """)

    # Add unique constraint to chat_id using batch mode for SQLite
    with op.batch_alter_table("notification_subscriptions") as batch_op:
        batch_op.create_unique_constraint("uq_notification_subscriptions_chat_id", ["chat_id"])


def downgrade() -> None:
    """Downgrade schema."""
    # Remove unique constraint using batch mode for SQLite
    with op.batch_alter_table("notification_subscriptions") as batch_op:
        batch_op.drop_constraint("uq_notification_subscriptions_chat_id", type_="unique")
