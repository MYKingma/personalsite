"""added name to recommendation

Revision ID: bb1ff3501b7f
Revises: ec654a2b0216
Create Date: 2020-06-17 16:59:15.887993

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bb1ff3501b7f'
down_revision = 'ec654a2b0216'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('recommendations', schema=None) as batch_op:
        batch_op.add_column(sa.Column('name', sa.String(length=128), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('recommendations', schema=None) as batch_op:
        batch_op.drop_column('name')

    # ### end Alembic commands ###