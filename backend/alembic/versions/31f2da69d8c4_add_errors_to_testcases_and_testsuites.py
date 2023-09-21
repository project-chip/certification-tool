"""Add Errors To TestCases and Testsuites

Revision ID: 31f2da69d8c4
Revises: 94d307a738ba
Create Date: 2021-05-11 23:05:08.049029

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "31f2da69d8c4"
down_revision = "94d307a738ba"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "testcaseexecution",
        sa.Column("errors", sa.ARRAY(sa.String(), dimensions=1), nullable=True),
    )
    op.add_column(
        "testsuiteexecution",
        sa.Column("errors", sa.ARRAY(sa.String(), dimensions=1), nullable=True),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("testsuiteexecution", "errors")
    op.drop_column("testcaseexecution", "errors")
    # ### end Alembic commands ###
