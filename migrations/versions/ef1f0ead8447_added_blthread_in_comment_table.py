"""added blthread in comment table

Revision ID: ef1f0ead8447
Revises: 75e35d7cb6a9
Create Date: 2020-07-31 16:27:31.595656

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ef1f0ead8447'
down_revision = '75e35d7cb6a9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('comments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('thread', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'comments', ['thread'], ['id'], ondelete='CASCADE')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('comments', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('thread')

    # ### end Alembic commands ###
