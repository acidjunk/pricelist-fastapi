"""empty message

Revision ID: 655d2e39050e
Revises: d5b0fe563e16
Create Date: 2019-09-17 23:17:03.543221

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "655d2e39050e"
down_revision = "d5b0fe563e16"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "shops_to_price",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=True),
        sa.Column("shop_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("price_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("use_half", sa.Boolean(), nullable=True),
        sa.Column("use_one", sa.Boolean(), nullable=True),
        sa.Column("two_five", sa.Boolean(), nullable=True),
        sa.Column("use_five", sa.Boolean(), nullable=True),
        sa.Column("use_joint", sa.Boolean(), nullable=True),
        sa.Column("use_piece", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
        sa.ForeignKeyConstraint(["price_id"], ["prices.id"]),
        sa.ForeignKeyConstraint(["shop_id"], ["shops.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_shops_to_price_category_id"), "shops_to_price", ["category_id"], unique=False)
    op.create_index(op.f("ix_shops_to_price_id"), "shops_to_price", ["id"], unique=False)
    op.create_index(op.f("ix_shops_to_price_price_id"), "shops_to_price", ["price_id"], unique=False)
    op.create_index(op.f("ix_shops_to_price_shop_id"), "shops_to_price", ["shop_id"], unique=False)
    op.drop_index("ix_prices_to_shops_category_id", table_name="prices_to_shops")
    op.drop_index("ix_prices_to_shops_id", table_name="prices_to_shops")
    op.drop_index("ix_prices_to_shops_price_id", table_name="prices_to_shops")
    op.drop_index("ix_prices_to_shops_shop_id", table_name="prices_to_shops")
    op.drop_table("prices_to_shops")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "prices_to_shops",
        sa.Column("id", postgresql.UUID(), autoincrement=False, nullable=False),
        sa.Column("shop_id", postgresql.UUID(), autoincrement=False, nullable=True),
        sa.Column("category_id", postgresql.UUID(), autoincrement=False, nullable=True),
        sa.Column("price_id", postgresql.UUID(), autoincrement=False, nullable=True),
        sa.Column("two_five", sa.BOOLEAN(), autoincrement=False, nullable=True),
        sa.Column("use_five", sa.BOOLEAN(), autoincrement=False, nullable=True),
        sa.Column("use_half", sa.BOOLEAN(), autoincrement=False, nullable=True),
        sa.Column("use_joint", sa.BOOLEAN(), autoincrement=False, nullable=True),
        sa.Column("use_one", sa.BOOLEAN(), autoincrement=False, nullable=True),
        sa.Column("use_piece", sa.BOOLEAN(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], name="prices_to_shops_category_id_fkey"),
        sa.ForeignKeyConstraint(["price_id"], ["prices.id"], name="prices_to_shops_price_id_fkey"),
        sa.ForeignKeyConstraint(["shop_id"], ["shops.id"], name="prices_to_shops_shop_id_fkey"),
        sa.PrimaryKeyConstraint("id", name="prices_to_shops_pkey"),
    )
    op.create_index("ix_prices_to_shops_shop_id", "prices_to_shops", ["shop_id"], unique=False)
    op.create_index("ix_prices_to_shops_price_id", "prices_to_shops", ["price_id"], unique=False)
    op.create_index("ix_prices_to_shops_id", "prices_to_shops", ["id"], unique=False)
    op.create_index("ix_prices_to_shops_category_id", "prices_to_shops", ["category_id"], unique=False)
    op.drop_index(op.f("ix_shops_to_price_shop_id"), table_name="shops_to_price")
    op.drop_index(op.f("ix_shops_to_price_price_id"), table_name="shops_to_price")
    op.drop_index(op.f("ix_shops_to_price_id"), table_name="shops_to_price")
    op.drop_index(op.f("ix_shops_to_price_category_id"), table_name="shops_to_price")
    op.drop_table("shops_to_price")
    # ### end Alembic commands ###
