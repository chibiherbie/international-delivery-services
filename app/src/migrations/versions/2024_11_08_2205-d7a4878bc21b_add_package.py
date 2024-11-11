"""add_package

Revision ID: d7a4878bc21b
Revises: 
Create Date: 2024-11-08 22:05:13.807532

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d7a4878bc21b"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "package_type",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "package",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("session_id", sa.String(length=255), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False),
        sa.Column("cost_in_usd", sa.Numeric(), nullable=False),
        sa.Column("delivery_cost", sa.Numeric(), nullable=True),
        sa.Column("delivery_company", sa.Integer(), nullable=True),
        sa.Column("package_type_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["package_type_id"],
            ["package_type.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.bulk_insert(
        sa.table(
            "package_type",
            sa.column("id", sa.Integer),
            sa.column("name", sa.String),
        ),
        [
            {"id": 1, "name": "Одежда"},
            {"id": 2, "name": "Электроника"},
            {"id": 3, "name": "Разное"},
        ]
    )


def downgrade() -> None:
    op.drop_table("package")
    op.drop_table("package_type")
