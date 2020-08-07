"""added name column to hidden table

Revision ID: 717270f1e937
Revises: d0c3b52ea7cc
Create Date: 2020-08-07 14:41:31.626220

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '717270f1e937'
down_revision = 'd0c3b52ea7cc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('hidden', schema=None) as batch_op:
        batch_op.add_column(sa.Column('name', sa.String(length=128), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('hidden', schema=None) as batch_op:
        batch_op.drop_column('name')

    # ### end Alembic commands ###