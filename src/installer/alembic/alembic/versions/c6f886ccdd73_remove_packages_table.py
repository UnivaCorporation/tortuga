"""remove packages table

Revision ID: c6f886ccdd73
Revises: d3c8cc11f603
Create Date: 2018-04-20 11:24:08.990606

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c6f886ccdd73'
down_revision = 'd3c8cc11f603'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table('packages')


def downgrade():
    pass
