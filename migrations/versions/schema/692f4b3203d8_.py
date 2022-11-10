"""empty message

Revision ID: 692f4b3203d8
Revises: 4f37d89acc0d
Create Date: 2022-04-22 13:17:42.021947

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "692f4b3203d8"
down_revision = "4f37d89acc0d"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("shops", sa.Column("last_pending_order", sa.String(length=255), nullable=True))
    op.add_column("shops", sa.Column("last_completed_order", sa.String(length=255), nullable=True))
    op.create_unique_constraint(None, "shops", ["last_completed_order"])
    op.create_unique_constraint(None, "shops", ["last_pending_order"])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "shops", type_="unique")
    op.drop_constraint(None, "shops", type_="unique")
    op.drop_column("shops", "last_completed_order")
    op.drop_column("shops", "last_pending_order")
    # ### end Alembic commands ###