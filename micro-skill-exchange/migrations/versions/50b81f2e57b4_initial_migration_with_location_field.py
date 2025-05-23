"""Initial migration with location field

Revision ID: 50b81f2e57b4
Revises: fcd7fbe9fa66
Create Date: 2025-04-27 18:13:36.585099

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '50b81f2e57b4'
down_revision = 'fcd7fbe9fa66'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('opportunity', schema=None) as batch_op:
        batch_op.add_column(sa.Column('location', sa.String(length=200), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('opportunity', schema=None) as batch_op:
        batch_op.drop_column('location')

    # ### end Alembic commands ###
