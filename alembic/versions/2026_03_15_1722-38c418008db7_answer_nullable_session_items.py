"""answer nullable session_items

Revision ID: 38c418008db7
Revises: e235ccb41396
Create Date: 2026-03-15 17:22:10.078921

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "38c418008db7"
down_revision: str | Sequence[str] | None = "e235ccb41396"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column("session_items", "answer", existing_type=sa.TEXT(), nullable=True)


def downgrade() -> None:
    op.alter_column("session_items", "answer", existing_type=sa.TEXT(), nullable=False)
