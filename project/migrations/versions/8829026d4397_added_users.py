"""added users

Revision ID: 8829026d4397
Revises: 035508da4318
Create Date: 2022-04-10 17:19:30.546961

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8829026d4397'
down_revision = '035508da4318'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('username', sa.String(length=30), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('surname', sa.String(length=50), nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.Column('roleId', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['roleId'], ['roles.id'], name=op.f('fk_users_roleId_roles'), ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_users')),
    sa.UniqueConstraint('username', name=op.f('uq_users_username'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users')
    # ### end Alembic commands ###