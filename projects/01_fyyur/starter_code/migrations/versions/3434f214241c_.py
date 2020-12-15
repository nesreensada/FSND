"""empty message

Revision ID: 3434f214241c
Revises: 0c3e4c971246
Create Date: 2020-12-15 22:09:21.725393

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3434f214241c'
down_revision = '0c3e4c971246'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('seeking_venue', sa.Boolean(), nullable=True))
    op.add_column('Artist', sa.Column('seeking_venue_description', sa.String(), nullable=True))
    op.drop_column('Artist', 'seeking_talent')
    op.drop_column('Artist', 'seeking_talent_description')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('seeking_talent_description', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('Artist', sa.Column('seeking_talent', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.drop_column('Artist', 'seeking_venue_description')
    op.drop_column('Artist', 'seeking_venue')
    # ### end Alembic commands ###