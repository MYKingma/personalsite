"""deleted errorlog table

Revision ID: d367532baa18
Revises: e309f76b2cf5
Create Date: 2020-07-07 15:24:55.521947

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'd367532baa18'
down_revision = 'e309f76b2cf5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('logs')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('logs',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('logger', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('level', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('trace', sa.VARCHAR(length=4096), autoincrement=False, nullable=True),
    sa.Column('msg', sa.VARCHAR(length=4096), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='logs_pkey')
    )
    # ### end Alembic commands ###
