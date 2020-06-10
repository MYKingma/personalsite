"""change upvote

Revision ID: b16b5c91ed43
Revises: a3949e468ce9
Create Date: 2020-05-18 22:08:25.577579

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b16b5c91ed43'
down_revision = 'a3949e468ce9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('reviews', schema=None) as batch_op:
        batch_op.drop_column('upvotes')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('reviews', schema=None) as batch_op:
        batch_op.add_column(sa.Column('upvotes', sa.INTEGER(), autoincrement=False, nullable=True))

    # ### end Alembic commands ###
