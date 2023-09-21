"""rename selected test cases

Revision ID: 136e7b39e9e8
Revises: 72989eaa90f6
Create Date: 2021-02-11 00:07:45.540498

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "136e7b39e9e8"
down_revision = "72989eaa90f6"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "testrunconfig", "selected_test_cases", new_column_name="selected_tests"
    )
    pass


def downgrade():
    op.alter_column(
        "testrunconfig", "selected_tests", new_column_name="selected_test_cases"
    )
    pass
