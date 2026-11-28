"""add post status

Revision ID: b731c8a2f904
Revises: be56774b673e
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "b731c8a2f904"
down_revision: str | Sequence[str] | None = "be56774b673e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("post", recreate="always") as batch_op:
        batch_op.add_column(
            sa.Column(
                "status",
                sa.Enum(
                    "published",
                    "draft",
                    name="post_status",
                    create_constraint=True,
                ),
                server_default="draft",
                nullable=False,
            )
        )

    # Посты с датой публикации считаем опубликованными
    op.execute(
        "UPDATE post SET status = 'published' WHERE published_at IS NOT NULL"
    )


def downgrade() -> None:
    with op.batch_alter_table("post", recreate="always") as batch_op:
        batch_op.drop_constraint("post_status", type_="check")
        batch_op.drop_column("status")
