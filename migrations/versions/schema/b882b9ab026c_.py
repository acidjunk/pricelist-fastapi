"""empty message

Revision ID: b882b9ab026c
Revises: dc089ecc2c38
Create Date: 2019-09-25 00:55:42.139151

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "b882b9ab026c"
down_revision = "dc089ecc2c38"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index("ix_categories_name", table_name="categories")
    op.drop_index("ix_shops_name", table_name="shops")
    op.create_index(op.f("ix_shops_name"), "shops", ["name"], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_shops_name"), table_name="shops")
    op.create_index("ix_shops_name", "shops", ["name"], unique=False)
    op.create_index("ix_categories_name", "categories", ["name"], unique=True)
    # ### end Alembic commands ###
