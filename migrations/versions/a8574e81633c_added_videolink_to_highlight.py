"""added videolink to highlight

Revision ID: a8574e81633c
Revises: 717270f1e937
Create Date: 2020-08-22 13:20:36.257226

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a8574e81633c'
down_revision = '717270f1e937'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('highlights', schema=None) as batch_op:
        batch_op.add_column(sa.Column('videolink', sa.Text(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('highlights', schema=None) as batch_op:
        batch_op.drop_column('videolink')

    # ### end Alembic commands ###