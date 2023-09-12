"""Enable description attribute

Revision ID: 079b491a5069
Revises: 66f5fdf75be8
Create Date: 2022-02-04 16:05:38.776481

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "079b491a5069"
down_revision = "66f5fdf75be8"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "testrunexecution", sa.Column("description", sa.String(), nullable=True)
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("testrunexecution", "description")
    # ### end Alembic commands ###
