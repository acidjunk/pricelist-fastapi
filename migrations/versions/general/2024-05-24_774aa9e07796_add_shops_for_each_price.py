"""Add an array of shops for each price.

Revision ID: 774aa9e07796
Revises: 98832770736b
Create Date: 2024-05-24 16:49:32.095197

"""
import sqlalchemy as sa
from alembic import op

from migrations.versions.helpers import update_price_with_shop_ids

# revision identifiers, used by Alembic.
revision = "774aa9e07796"
down_revision = "98832770736b"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()

    # Fetch all current entries in the prices table

    shops = conn.execute(sa.text("SELECT id FROM shops")).fetchall()
    shop_ids = [shop.id for shop in shops]

    prices = conn.execute(sa.text("SELECT * FROM prices")).fetchall()

    for price in prices:
        price_id = price.id

        if shop_ids:
            update_price_with_shop_ids(conn, shop_ids, price_id)


def downgrade() -> None:
    conn = op.get_bind()

    # Clear the `shop_ids` field if needing to downgrade
    conn.execute(sa.text("UPDATE prices SET shop_ids = NULL"))
