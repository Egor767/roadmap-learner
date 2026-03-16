"""delete user prefix

Revision ID: 3c8978a5448a
Revises: 38c418008db7
Create Date: 2026-03-16 18:09:36.720123

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3c8978a5448a"
down_revision: str | Sequence[str] | None = "38c418008db7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


from sqlalchemy.dialects import postgresql


def upgrade() -> None:
    op.create_table(
        "card_progress",
        sa.Column(
            "status",
            postgresql.ENUM("KNOWN", "UNKNOWN", "REPEAT", name="card_status", create_type=False),
            nullable=False,
        ),
        # остальные колонки...
    )
    op.create_table(
        "question_progress",
        sa.Column(
            "status",
            postgresql.ENUM("KNOWN", "UNKNOWN", "REPEAT", name="question_status", create_type=False),
            nullable=False,
        ),
        # остальные колонки...
    )
    op.drop_table("user_card_progress")
    op.drop_table("user_question_progress")


def downgrade() -> None:
    op.create_table("user_question_progress", ...)
    op.create_table("user_card_progress", ...)

    op.drop_table("question_progress")
    op.drop_table("card_progress")
