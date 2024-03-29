"""changed refresh tokens

Revision ID: 77d6d7d91958
Revises: b1490e329213
Create Date: 2022-04-15 22:33:30.606370

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '77d6d7d91958'
down_revision = 'b1490e329213'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(op.f('uq_refresh_tokens_user_id'), 'refresh_tokens', ['user_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f('uq_refresh_tokens_user_id'), 'refresh_tokens', type_='unique')
    # ### end Alembic commands ###
