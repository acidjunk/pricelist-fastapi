"""empty message

Revision ID: 86f5375d4011
Revises: d4ce7e1204cd
Create Date: 2021-01-19 15:04:03.146408

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '86f5375d4011'
down_revision = 'd4ce7e1204cd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('categories', sa.Column('color', sa.String(length=20), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('categories', 'color')
    # ### end Alembic commands ###
