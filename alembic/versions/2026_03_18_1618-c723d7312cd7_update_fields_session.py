"""update fields session

Revision ID: c723d7312cd7
Revises: 0bc06a47106c
Create Date: 2026-03-18 16:18:55.150048

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c723d7312cd7"
down_revision: str | Sequence[str] | None = "0bc06a47106c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TYPE knowledge_status RENAME TO card_status")
    op.add_column("sessions", sa.Column("repeat_answers", sa.Integer(), nullable=False, server_default="0"))
    op.alter_column("sessions", "repeat_answers", server_default=None)
    op.add_column("sessions", sa.Column("module_id", sa.Uuid(), nullable=True))
    op.create_foreign_key(
        op.f("fk_sessions_module_id_modules"), "sessions", "modules", ["module_id"], ["id"], ondelete="CASCADE"
    )
    op.drop_column("sessions", "block_id")
    op.drop_column("sessions", "review_answers")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column("sessions", sa.Column("review_answers", sa.INTEGER(), autoincrement=False, nullable=False))
    op.add_column("sessions", sa.Column("block_id", sa.UUID(), autoincrement=False, nullable=True))
    op.drop_constraint(op.f("fk_sessions_module_id_modules"), "sessions", type_="foreignkey")
    op.drop_column("sessions", "module_id")
    op.drop_column("sessions", "repeat_answers")
    op.execute("ALTER TYPE card_status RENAME TO knowledge_status")
