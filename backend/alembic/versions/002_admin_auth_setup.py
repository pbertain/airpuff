"""Add admin auth fields and route template tables.

Revision ID: 002
Revises: 001
Create Date: 2026-06-23 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("role", sa.String(length=32), nullable=False, server_default="user"),
    )
    op.add_column(
        "airports",
        sa.Column(
            "is_monitored",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )

    op.create_table(
        "route_templates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_route_templates_id"), "route_templates", ["id"], unique=False)

    op.create_table(
        "route_template_airports",
        sa.Column("route_template_id", sa.Integer(), nullable=False),
        sa.Column("airport_id", sa.Integer(), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["airport_id"], ["airports.id"]),
        sa.ForeignKeyConstraint(["route_template_id"], ["route_templates.id"]),
        sa.PrimaryKeyConstraint("route_template_id", "airport_id"),
    )

    op.alter_column("users", "role", server_default=None)
    op.alter_column("airports", "is_monitored", server_default=None)
    op.alter_column("route_templates", "is_active", server_default=None)


def downgrade() -> None:
    op.drop_table("route_template_airports")
    op.drop_index(op.f("ix_route_templates_id"), table_name="route_templates")
    op.drop_table("route_templates")
    op.drop_column("airports", "is_monitored")
    op.drop_column("users", "role")
