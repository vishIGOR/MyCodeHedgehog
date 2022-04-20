"""added topic model

Revision ID: 64747df10f1b
Revises: 77d6d7d91958
Create Date: 2022-04-20 20:20:54.746308

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '64747df10f1b'
down_revision = '77d6d7d91958'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('topics',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('description', sa.String(length=500), nullable=False),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['parent_id'], ['topics.id'], name=op.f('fk_topics_parent_id_topics'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_topics')),
    sa.UniqueConstraint('name', name=op.f('uq_topics_name'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('topics')
    # ### end Alembic commands ###
