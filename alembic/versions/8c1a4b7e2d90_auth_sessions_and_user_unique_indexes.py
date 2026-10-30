"""Add revocable auth sessions and normalized user identity indexes.

Revision ID: 8c1a4b7e2d90
Revises: 60eb59bdb78a
Create Date: 2026-10-29
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8c1a4b7e2d90"
down_revision: Union[str, Sequence[str], None] = "60eb59bdb78a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    connection = op.get_bind()

    duplicate_email_exists = connection.execute(
        sa.text(
            """
            SELECT EXISTS (
                SELECT 1
                FROM users
                GROUP BY lower(trim(email))
                HAVING count(*) > 1
            )
            """
        )
    ).scalar_one()
    duplicate_username_exists = connection.execute(
        sa.text(
            """
            SELECT EXISTS (
                SELECT 1
                FROM users
                GROUP BY lower(trim(username))
                HAVING count(*) > 1
            )
            """
        )
    ).scalar_one()

    if duplicate_email_exists or duplicate_username_exists:
        raise RuntimeError(
            "Cannot add normalized unique user indexes: duplicate email or "
            "username values exist. Resolve duplicate accounts, then retry."
        )

    op.execute(
        "CREATE UNIQUE INDEX uq_users_email_normalized "
        "ON users (lower(trim(email)))"
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_users_username_normalized "
        "ON users (lower(trim(username)))"
    )

    op.create_table(
        "auth_sessions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index(
        "ix_auth_sessions_user_id",
        "auth_sessions",
        ["user_id"],
    )
    op.create_index(
        "ix_auth_sessions_expires_at",
        "auth_sessions",
        ["expires_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_auth_sessions_expires_at", table_name="auth_sessions")
    op.drop_index("ix_auth_sessions_user_id", table_name="auth_sessions")
    op.drop_table("auth_sessions")
    op.execute("DROP INDEX uq_users_username_normalized")
    op.execute("DROP INDEX uq_users_email_normalized")
