"""initial

Revision ID: df530e0ea561
Revises: 
Create Date: 2022-01-10 21:57:30.468851

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'df530e0ea561'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('knowledge_area',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('code', sa.BigInteger(), nullable=True),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tg_id', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('tg_id')
    )
    op.create_table('zno',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('grades',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('owner_id', sa.Integer(), nullable=True),
    sa.Column('zno_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['zno_id'], ['zno.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('speciality',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('program', sa.String(length=255), nullable=True),
    sa.Column('min_rate_budget', sa.Float(), nullable=True),
    sa.Column('min_rate_pay', sa.Float(), nullable=True),
    sa.Column('area_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['area_id'], ['knowledge_area.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('coefficient',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('speciality_id', sa.Integer(), nullable=True),
    sa.Column('zno_id', sa.Integer(), nullable=True),
    sa.Column('coefficient', sa.Float(), nullable=True),
    sa.Column('required', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['speciality_id'], ['speciality.id'], ),
    sa.ForeignKeyConstraint(['zno_id'], ['zno.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('coefficient')
    op.drop_table('speciality')
    op.drop_table('grades')
    op.drop_table('zno')
    op.drop_table('users')
    op.drop_table('knowledge_area')
    # ### end Alembic commands ###
