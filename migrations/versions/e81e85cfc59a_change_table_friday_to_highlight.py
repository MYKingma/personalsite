"""change table friday to highlight

Revision ID: e81e85cfc59a
Revises: 9c7c437a48d6
Create Date: 2020-06-20 15:31:17.966870

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'e81e85cfc59a'
down_revision = '9c7c437a48d6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('highlights',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('place_id', sa.String(length=128), nullable=False),
    sa.Column('week', sa.DateTime(), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('friday_tips')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('friday_tips',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('place_id', sa.VARCHAR(length=128), autoincrement=False, nullable=False),
    sa.Column('date', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('description', sa.TEXT(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='friday_tips_pkey')
    )
    op.drop_table('highlights')
    # ### end Alembic commands ###