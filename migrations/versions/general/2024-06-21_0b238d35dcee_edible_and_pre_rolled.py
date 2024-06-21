"""edible_and_pre_rolled.

Revision ID: 0b238d35dcee
Revises: efb31a3c4de3
Create Date: 2024-06-21 16:57:00.312227

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0b238d35dcee"
down_revision = "efb31a3c4de3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("prices", sa.Column("edible", sa.JSON(), nullable=True))
    op.add_column("prices", sa.Column("pre_rolled_joints", sa.JSON(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("prices", "pre_rolled_joints")
    op.drop_column("prices", "edible")
    # ### end Alembic commands ###
