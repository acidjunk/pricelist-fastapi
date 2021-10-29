"""empty message

Revision ID: 62e315123504
Revises: b98ea2a3d8ea
Create Date: 2019-12-06 22:31:48.169179

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "62e315123504"
down_revision = "b98ea2a3d8ea"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("kinds", sa.Column("complete", sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("kinds", "complete")
    # ### end Alembic commands ###
