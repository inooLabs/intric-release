"""cleanup after tenants id swap
Revision ID: 2f35cd0ec26b
Revises: eaba304928e5
Create Date: 2024-07-02 17:37:57.094951
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic
revision = "2f35cd0ec26b"
down_revision = "eaba304928e5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "allowed_origins", "tenant_id", existing_type=sa.UUID(), nullable=False
    )
    op.alter_column(
        "completion_model_settings",
        "tenant_id",
        existing_type=sa.UUID(),
        nullable=False,
    )
    op.alter_column("crawl_runs", "tenant_id", existing_type=sa.UUID(), nullable=False)
    op.alter_column(
        "embedding_model_settings", "tenant_id", existing_type=sa.UUID(), nullable=False
    )
    op.alter_column("files", "tenant_id", existing_type=sa.UUID(), nullable=False)
    op.alter_column("groups", "tenant_id", existing_type=sa.UUID(), nullable=False)
    op.alter_column("roles", "tenant_id", existing_type=sa.UUID(), nullable=False)
    op.create_unique_constraint(
        "roles_name_tenant_unique", "roles", ["name", "tenant_id"]
    )
    op.alter_column("user_groups", "tenant_id", existing_type=sa.UUID(), nullable=False)
    op.create_unique_constraint(
        "user_groups_name_tenant_unique", "user_groups", ["name", "tenant_id"]
    )
    op.alter_column("users", "tenant_id", existing_type=sa.UUID(), nullable=False)
    op.create_unique_constraint(
        "users_email_tenant_unique", "users", ["email", "tenant_id"]
    )
    op.create_unique_constraint(
        "users_username_tenant_unique", "users", ["username", "tenant_id"]
    )
    op.alter_column("websites", "tenant_id", existing_type=sa.UUID(), nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("websites", "tenant_id", existing_type=sa.UUID(), nullable=True)
    op.drop_constraint("users_username_tenant_unique", "users", type_="unique")
    op.drop_constraint("users_email_tenant_unique", "users", type_="unique")
    op.alter_column("users", "tenant_id", existing_type=sa.UUID(), nullable=True)
    op.drop_constraint("user_groups_name_tenant_unique", "user_groups", type_="unique")
    op.alter_column("user_groups", "tenant_id", existing_type=sa.UUID(), nullable=True)
    op.drop_constraint("roles_name_tenant_unique", "roles", type_="unique")
    op.alter_column("roles", "tenant_id", existing_type=sa.UUID(), nullable=True)
    op.alter_column("groups", "tenant_id", existing_type=sa.UUID(), nullable=True)
    op.alter_column("files", "tenant_id", existing_type=sa.UUID(), nullable=True)
    op.alter_column(
        "embedding_model_settings", "tenant_id", existing_type=sa.UUID(), nullable=True
    )
    op.alter_column("crawl_runs", "tenant_id", existing_type=sa.UUID(), nullable=True)
    op.alter_column(
        "completion_model_settings", "tenant_id", existing_type=sa.UUID(), nullable=True
    )
    op.alter_column(
        "allowed_origins", "tenant_id", existing_type=sa.UUID(), nullable=True
    )
    # ### end Alembic commands ###
