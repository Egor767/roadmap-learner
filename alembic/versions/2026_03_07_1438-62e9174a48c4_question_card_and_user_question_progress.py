"""question_card and user_question_progress

Revision ID: 62e9174a48c4
Revises: b19f35d949f2
Create Date: 2026-03-07 14:38:18.686223

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "62e9174a48c4"
down_revision: str | Sequence[str] | None = "b19f35d949f2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Удаляем устаревшие enum-ы
    op.execute("DROP TYPE IF EXISTS block_status")
    op.execute("DROP TYPE IF EXISTS card_status")
    op.execute("DROP TYPE IF EXISTS roadmap_status")

    op.create_table(
        "question_cards",
        sa.Column("question_id", sa.Uuid(), nullable=False),
        sa.Column("card_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["card_id"],
            ["cards.id"],
            name=op.f("fk_question_cards_card_id_cards"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["question_id"],
            ["questions.id"],
            name=op.f("fk_question_cards_question_id_questions"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("question_id", "card_id", name=op.f("pk_question_cards")),
    )
    op.create_table(
        "user_question_progress",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("question_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.Enum("KNOWN", "UNKNOWN", "REVIEW", name="question_status"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["question_id"],
            ["questions.id"],
            name=op.f("fk_user_question_progress_question_id_questions"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_user_question_progress_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("user_id", "question_id", name=op.f("pk_user_question_progress")),
    )


def downgrade() -> None:
    op.drop_table("user_question_progress")
    op.execute("DROP TYPE IF EXISTS question_status")
    op.drop_table("question_cards")

    # Восстанавливаем удалённые enum-ы
    op.execute("CREATE TYPE block_status AS ENUM ()")
    op.execute("CREATE TYPE card_status AS ENUM ()")
    op.execute("CREATE TYPE roadmap_status AS ENUM ()")
