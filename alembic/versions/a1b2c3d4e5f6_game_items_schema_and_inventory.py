"""game items schema and inventory

Revision ID: a1b2c3d4e5f6
Revises: 8990993397fc
Create Date: 2026-06-21 23:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "8990993397fc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("items", schema=None) as batch_op:
        batch_op.add_column(sa.Column("item_type", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("rarity", sa.String(), server_default="common"))
        batch_op.add_column(sa.Column("potency_boost", sa.Integer(), server_default="0"))
        batch_op.add_column(sa.Column("icon", sa.String(), nullable=True))
        batch_op.drop_column("price")
        batch_op.drop_column("is_active")
        batch_op.drop_column("category_id")

    op.execute("UPDATE items SET item_type = 'ingredient' WHERE item_type IS NULL")

    with op.batch_alter_table("items", schema=None) as batch_op:
        batch_op.alter_column("item_type", nullable=False)
        batch_op.create_unique_constraint("uq_items_name", ["name"])

    op.create_table(
        "inventory",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("player_id", sa.Integer(), nullable=False),
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), server_default="1"),
        sa.Column("quality", sa.String(), server_default="Обычный"),
        sa.Column("source_bed_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)")),
        sa.ForeignKeyConstraint(["player_id"], ["players.id"]),
        sa.ForeignKeyConstraint(["item_id"], ["items.id"]),
        sa.ForeignKeyConstraint(["source_bed_id"], ["garden_beds.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_inventory_id"), "inventory", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_inventory_id"), table_name="inventory")
    op.drop_table("inventory")

    with op.batch_alter_table("items", schema=None) as batch_op:
        batch_op.drop_constraint("uq_items_name", type_="unique")
        batch_op.add_column(sa.Column("category_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("is_active", sa.Boolean(), server_default="1"))
        batch_op.add_column(sa.Column("price", sa.Numeric(precision=10, scale=2), server_default="0"))
        batch_op.create_foreign_key("items_category_id_fkey", "categories", ["category_id"], ["id"])
        batch_op.drop_column("icon")
        batch_op.drop_column("potency_boost")
        batch_op.drop_column("rarity")
        batch_op.drop_column("item_type")
