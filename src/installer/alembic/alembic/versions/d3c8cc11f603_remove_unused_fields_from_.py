"""Remove unused fields from hardwareprofiles table

Revision ID: d3c8cc11f603
Revises: c39f7655419a
Create Date: 2018-04-14 11:46:17.352049

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd3c8cc11f603'
down_revision = 'c39f7655419a'
branch_labels = None
depends_on = None


def drop_column_sqlite(tablename, columns):
    """ column dropping functionality for SQLite """

    # we need copy to make a deep copy of the column attributes
    from copy import copy

    # get the db engine and reflect database tables
    engine = op.get_bind()
    meta = sa.MetaData(bind=engine)
    meta.reflect()

    # create a select statement from the old table
    old_table = meta.tables[tablename]
    select = sa.sql.select([c for c in old_table.c if c.name not in columns])

    # get remaining columns without table attribute attached
    remaining_columns = [copy(c) for c in old_table.columns
            if c.name not in columns]
    for column in remaining_columns:
        column.table = None

    # create a temporary new table
    new_tablename = '{0}_new'.format(tablename)
    op.create_table(new_tablename, *remaining_columns)
    meta.reflect()
    new_table = meta.tables[new_tablename]

    # copy data from old table
    insert = sa.sql.insert(new_table).from_select(
            [c.name for c in remaining_columns], select)
    engine.execute(insert)

    # drop the old table and rename the new table to take the old tables
    # position
    op.drop_table(tablename)
    op.rename_table(new_tablename, tablename)


def upgrade():
    drop_column_sqlite('hardwareprofiles', 'mcastEnabled')
    drop_column_sqlite('hardwareprofiles', 'bcastEnabled')
    drop_column_sqlite('hardwareprofiles', 'maxUnits')


def downgrade():
    op.add_column('hardwareprofiles', sa.Column('mcastEnabled', sa.Boolean))
    op.add_column('hardwareprofiles', sa.Column('bcastEnabled', sa.Boolean))
    op.add_column('hardwareprofiles', sa.Column('maxUnits', sa.Integer))
