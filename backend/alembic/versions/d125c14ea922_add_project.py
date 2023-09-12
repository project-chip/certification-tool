"""Add Project

Revision ID: d125c14ea922
Revises: 079dfe8e3e03
Create Date: 2021-06-25 13:08:15.540706

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "d125c14ea922"
down_revision = "079dfe8e3e03"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "project",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("dut_vid", sa.String(), nullable=True),
        sa.Column("dut_pid", sa.String(), nullable=True),
        sa.Column(
            "dut_type",
            sa.Enum("CONTROLLER", "APP", "ACCESSORY", name="duttype"),
            nullable=False,
        ),
        sa.Column("wifi_ssid", sa.String(), nullable=True),
        sa.Column("wifi_password", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_project")),
    )
    op.create_index(op.f("ix_project_id"), "project", ["id"], unique=False)
    op.add_column(
        "testrunexecution", sa.Column("project_id", sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        op.f("fk_testrunexecution_project_id_project"),
        "testrunexecution",
        "project",
        ["project_id"],
        ["id"],
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(
        op.f("fk_testrunexecution_project_id_project"),
        "testrunexecution",
        type_="foreignkey",
    )
    op.drop_column("testrunexecution", "project_id")
    op.drop_index(op.f("ix_project_id"), table_name="project")
    op.drop_table("project")
    # ### end Alembic commands ###
