"""make_uq_question_block_order_deferrable

Revision ID: ad4fb0c75854
Revises: 9294eb271afb
Create Date: 2026-03-12 21:15:28.079559

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ad4fb0c75854"
down_revision: str | Sequence[str] | None = "9294eb271afb"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint("uq_question_block_order", "questions", type_="unique")
    op.execute("""
        ALTER TABLE questions
        ADD CONSTRAINT uq_question_block_order
        UNIQUE (block_id, order_index)
        DEFERRABLE INITIALLY DEFERRED
    """)


def downgrade() -> None:
    op.drop_constraint("uq_question_block_order", "questions", type_="unique")
    op.execute("""
        ALTER TABLE questions
        ADD CONSTRAINT uq_question_block_order
        UNIQUE (block_id, order_index)
    """)
