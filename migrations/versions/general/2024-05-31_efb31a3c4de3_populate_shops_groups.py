"""Populate shops groups.

Revision ID: efb31a3c4de3
Revises: 5cf8f01eda8b
Create Date: 2024-05-31 20:29:31.041111

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID, ARRAY
import uuid

# revision identifiers, used by Alembic.
revision = "efb31a3c4de3"
down_revision = "5cf8f01eda8b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    shops = conn.execute(sa.text("SELECT id FROM shops")).fetchall()
    shop_ids = [shop.id for shop in shops]

    shop_group_id = uuid.uuid4()

    conn.execute(
        sa.text("INSERT INTO shop_groups (id, name, shop_ids) VALUES (:id, :name, :shop_ids)"),
        {"id": shop_group_id, "name": "Maastricht", "shop_ids": shop_ids},
    )

    conn.execute(
        sa.text("UPDATE prices SET shop_group_id = :shop_group_id"),
        {"shop_group_id": shop_group_id},  # Use the same UUID here
    )


def downgrade() -> None:
    pass
