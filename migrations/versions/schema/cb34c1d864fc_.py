"""empty message

Revision ID: cb34c1d864fc
Revises: fced7eea1ca7
Create Date: 2019-09-18 00:37:44.141229

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "cb34c1d864fc"
down_revision = "fced7eea1ca7"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("flavors", sa.Column("color", sa.String(length=20), nullable=True))
    op.drop_column("flavors", "color2")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("flavors", sa.Column("color2", sa.VARCHAR(length=20), autoincrement=False, nullable=True))
    op.drop_column("flavors", "color")
    # ### end Alembic commands ###