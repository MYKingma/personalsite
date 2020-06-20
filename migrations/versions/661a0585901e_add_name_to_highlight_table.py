"""add name to highlight table

Revision ID: 661a0585901e
Revises: e81e85cfc59a
Create Date: 2020-06-20 15:39:29.481868

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '661a0585901e'
down_revision = 'e81e85cfc59a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('highlights', schema=None) as batch_op:
        batch_op.add_column(sa.Column('name', sa.String(length=128), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('highlights', schema=None) as batch_op:
        batch_op.drop_column('name')

    # ### end Alembic commands ###