"""added title column with blog

Revision ID: 66b9b0caedd2
Revises: 183dd53cddbc
Create Date: 2020-06-20 14:43:56.084543

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '66b9b0caedd2'
down_revision = '183dd53cddbc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('blog', schema=None) as batch_op:
        batch_op.add_column(sa.Column('title', sa.String(length=128), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('blog', schema=None) as batch_op:
        batch_op.drop_column('title')

    # ### end Alembic commands ###
