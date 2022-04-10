"""changed users role_id

Revision ID: 443b821478c1
Revises: 25a3ee0f9951
Create Date: 2022-04-11 02:19:53.722244

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '443b821478c1'
down_revision = '25a3ee0f9951'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('role_id', sa.Integer(), nullable=True))
    op.drop_constraint('fk_users_roleId_roles', 'users', type_='foreignkey')
    op.create_foreign_key(op.f('fk_users_role_id_roles'), 'users', 'roles', ['role_id'], ['id'], ondelete='SET NULL')
    op.drop_column('users', 'roleId')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('roleId', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(op.f('fk_users_role_id_roles'), 'users', type_='foreignkey')
    op.create_foreign_key('fk_users_roleId_roles', 'users', 'roles', ['roleId'], ['id'], ondelete='SET NULL')
    op.drop_column('users', 'role_id')
    # ### end Alembic commands ###