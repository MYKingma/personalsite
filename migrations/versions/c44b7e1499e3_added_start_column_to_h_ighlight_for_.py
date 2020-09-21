"""added start column to h
ighlight for video

Revision ID: c44b7e1499e3
Revises: b04fcc0e2dc2
Create Date: 2020-09-21 15:56:36.153035

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c44b7e1499e3'
down_revision = 'b04fcc0e2dc2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('highlights', schema=None) as batch_op:
        batch_op.add_column(sa.Column('videostart', sa.Text(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('highlights', schema=None) as batch_op:
        batch_op.drop_column('videostart')

    # ### end Alembic commands ###
