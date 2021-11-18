"""empty message

Revision ID: d4ce7e1204cd
Revises: b34e3e216a68
Create Date: 2020-12-04 11:46:50.021472

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "d4ce7e1204cd"
down_revision = "b34e3e216a68"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("categories", sa.Column("icon", sa.String(length=60), nullable=True))
    op.add_column("main_categories", sa.Column("icon", sa.String(length=60), nullable=True))
    op.add_column("shops_to_price", sa.Column("new", sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("shops_to_price", "new")
    op.drop_column("main_categories", "icon")
    op.drop_column("categories", "icon")
    # ### end Alembic commands ###