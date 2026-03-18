"""rename card to concept and block to module

Revision ID: 0bc06a47106c
Revises: 3c8978a5448a
Create Date: 2026-03-18 10:16:14.210433

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0bc06a47106c"
down_revision: str | Sequence[str] | None = "3c8978a5448a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TYPE card_status RENAME TO knowledge_status")

    op.rename_table("modules", "modules")
    op.execute("ALTER TABLE modules RENAME CONSTRAINT pk_blocks TO pk_modules")
    op.execute("ALTER TABLE modules RENAME CONSTRAINT fk_blocks_roadmap_id_roadmaps TO fk_modules_roadmap_id_roadmaps")
    op.execute("ALTER TABLE modules RENAME CONSTRAINT uq_block_roadmap_order TO uq_module_roadmap_order")
    op.execute("ALTER TABLE modules RENAME CONSTRAINT uq_block_roadmap_title TO uq_module_roadmap_title")
    op.execute("ALTER INDEX ix_block_roadmap_order RENAME TO ix_module_roadmap_order")

    op.alter_column("questions", "module_id", new_column_name="module_id")
    op.execute("ALTER TABLE questions RENAME CONSTRAINT fk_questions_block_id_blocks TO fk_questions_module_id_modules")
    op.execute("ALTER INDEX ix_question_block_order RENAME TO ix_question_module_order")
    op.execute("ALTER TABLE questions RENAME CONSTRAINT uq_question_block_order TO uq_question_module_order")
    op.execute("ALTER TABLE questions RENAME CONSTRAINT uq_question_block_question TO uq_question_module_question")

    op.rename_table("concepts", "concepts")
    op.execute("ALTER TABLE concepts RENAME CONSTRAINT pk_cards TO pk_concepts")
    op.execute("ALTER TABLE concepts RENAME CONSTRAINT fk_cards_roadmap_id_roadmaps TO fk_concepts_roadmap_id_roadmaps")
    op.execute("ALTER TABLE concepts RENAME CONSTRAINT uq_card_roadmap_term TO uq_concept_roadmap_term")

    op.rename_table("question_card", "question_concept")
    op.alter_column("question_concept", "card_id", new_column_name="concept_id")
    op.execute("ALTER TABLE question_concept RENAME CONSTRAINT pk_question_card TO pk_question_concept")
    op.execute(
        "ALTER TABLE question_concept RENAME CONSTRAINT fk_question_card_card_id_cards TO fk_question_concept_concept_id_concepts"
    )
    op.execute(
        "ALTER TABLE question_concept RENAME CONSTRAINT fk_question_card_question_id_questions TO fk_question_concept_question_id_questions"
    )

    op.rename_table("card_progress", "concept_progress")
    op.add_column(
        "concept_progress",
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.add_column(
        "concept_progress",
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.add_column("concept_progress", sa.Column("user_id", sa.Uuid(), nullable=False))
    op.add_column("concept_progress", sa.Column("concept_id", sa.Uuid(), nullable=False))
    op.create_primary_key(op.f("pk_concept_progress"), "concept_progress", ["user_id", "concept_id"])
    op.create_foreign_key(
        op.f("fk_concept_progress_user_id_users"), "concept_progress", "users", ["user_id"], ["id"], ondelete="CASCADE"
    )
    op.create_foreign_key(
        op.f("fk_concept_progress_concept_id_concepts"),
        "concept_progress",
        "concepts",
        ["concept_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.add_column(
        "question_progress",
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.add_column(
        "question_progress",
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.add_column("question_progress", sa.Column("user_id", sa.Uuid(), nullable=False))
    op.add_column("question_progress", sa.Column("question_id", sa.Uuid(), nullable=False))
    op.create_primary_key(op.f("pk_question_progress"), "question_progress", ["user_id", "question_id"])
    op.create_foreign_key(
        op.f("fk_question_progress_user_id_users"),
        "question_progress",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        op.f("fk_question_progress_question_id_questions"),
        "question_progress",
        "questions",
        ["question_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(op.f("fk_question_progress_question_id_questions"), "question_progress", type_="foreignkey")
    op.drop_constraint(op.f("fk_question_progress_user_id_users"), "question_progress", type_="foreignkey")
    op.drop_constraint(op.f("pk_question_progress"), "question_progress", type_="primary")
    op.drop_column("question_progress", "question_id")
    op.drop_column("question_progress", "user_id")
    op.drop_column("question_progress", "updated_at")
    op.drop_column("question_progress", "created_at")

    op.drop_constraint(op.f("fk_concept_progress_concept_id_concepts"), "concept_progress", type_="foreignkey")
    op.drop_constraint(op.f("fk_concept_progress_user_id_users"), "concept_progress", type_="foreignkey")
    op.drop_constraint(op.f("pk_concept_progress"), "concept_progress", type_="primary")
    op.drop_column("concept_progress", "concept_id")
    op.drop_column("concept_progress", "user_id")
    op.drop_column("concept_progress", "updated_at")
    op.drop_column("concept_progress", "created_at")
    op.rename_table("concept_progress", "card_progress")

    op.execute(
        "ALTER TABLE question_concept RENAME CONSTRAINT fk_question_concept_question_id_questions TO fk_question_card_question_id_questions"
    )
    op.execute(
        "ALTER TABLE question_concept RENAME CONSTRAINT fk_question_concept_concept_id_concepts TO fk_question_card_card_id_cards"
    )
    op.execute("ALTER TABLE question_concept RENAME CONSTRAINT pk_question_concept TO pk_question_card")
    op.alter_column("question_concept", "concept_id", new_column_name="card_id")
    op.rename_table("question_concept", "question_card")

    op.execute("ALTER TABLE concepts RENAME CONSTRAINT uq_concept_roadmap_term TO uq_card_roadmap_term")
    op.execute("ALTER TABLE concepts RENAME CONSTRAINT fk_concepts_roadmap_id_roadmaps TO fk_cards_roadmap_id_roadmaps")
    op.execute("ALTER TABLE concepts RENAME CONSTRAINT pk_concepts TO pk_cards")
    op.rename_table("concepts", "concepts")

    op.execute("ALTER TABLE questions RENAME CONSTRAINT uq_question_module_question TO uq_question_block_question")
    op.execute("ALTER TABLE questions RENAME CONSTRAINT uq_question_module_order TO uq_question_block_order")
    op.execute("ALTER INDEX ix_question_module_order RENAME TO ix_question_block_order")
    op.execute("ALTER TABLE questions RENAME CONSTRAINT fk_questions_module_id_modules TO fk_questions_block_id_blocks")
    op.alter_column("questions", "module_id", new_column_name="module_id")

    op.execute("ALTER INDEX ix_module_roadmap_order RENAME TO ix_block_roadmap_order")
    op.execute("ALTER TABLE modules RENAME CONSTRAINT uq_module_roadmap_title TO uq_block_roadmap_title")
    op.execute("ALTER TABLE modules RENAME CONSTRAINT uq_module_roadmap_order TO uq_block_roadmap_order")
    op.execute("ALTER TABLE modules RENAME CONSTRAINT fk_modules_roadmap_id_roadmaps TO fk_blocks_roadmap_id_roadmaps")
    op.execute("ALTER TABLE modules RENAME CONSTRAINT pk_modules TO pk_blocks")
    op.rename_table("modules", "modules")

    op.execute("ALTER TYPE knowledge_status RENAME TO card_status")
