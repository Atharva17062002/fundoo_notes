"""Created notes model

Revision ID: 61291af6593d
Revises: 8365a247546d
Create Date: 2024-02-14 10:59:30.313302

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '61291af6593d'
down_revision = '8365a247546d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('notes',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('title', sa.String(length=50), nullable=True),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('color', sa.String(length=20), nullable=True),
    sa.Column('reminder', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('notes')
    # ### end Alembic commands ###
