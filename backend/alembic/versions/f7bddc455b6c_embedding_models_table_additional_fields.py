"""embedding models table additional fields
Revision ID: f7bddc455b6c
Revises: 45a36acc858a
Create Date: 2024-05-22 16:03:14.277682
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic
revision = "f7bddc455b6c"
down_revision = "45a36acc858a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "embedding_models", sa.Column("description", sa.String(), nullable=True)
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("embedding_models", "description")
    # ### end Alembic commands ###
