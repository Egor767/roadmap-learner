"""add auto_check into session and create session_item table

Revision ID: e235ccb41396
Revises: 7ee7539bde30
Create Date: 2026-03-14 20:25:09.585424

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e235ccb41396"
down_revision: str | Sequence[str] | None = "7ee7539bde30"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TYPE question_status RENAME VALUE 'REVIEW' TO 'REPEAT'")
    op.create_table(
        "session_items",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("session_id", sa.UUID(), nullable=False),
        sa.Column("question_id", sa.UUID(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("hint", sa.Boolean(), server_default="false", nullable=False),
        sa.Column(
            "result",
            ENUM("KNOWN", "UNKNOWN", "REPEAT", name="question_status", create_type=False),
            nullable=True,
        ),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["question_id"],
            ["questions.id"],
            name=op.f("fk_session_items_question_id_questions"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["sessions.id"],
            name=op.f("fk_session_items_session_id_sessions"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_session_items")),
    )
    op.add_column("sessions", sa.Column("auto_check", sa.Boolean(), server_default="false", nullable=False))


def downgrade() -> None:
    op.execute("ALTER TYPE question_status RENAME VALUE 'REPEAT' TO 'REVIEW'")
    op.drop_column("sessions", "auto_check")
    op.drop_table("session_items")
