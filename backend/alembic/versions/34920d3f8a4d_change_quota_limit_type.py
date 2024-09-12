"""change quota limit type
Revision ID: 34920d3f8a4d
Revises: bfa43d57de38
Create Date: 2024-08-19 15:57:08.099495
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic
revision = '34920d3f8a4d'
down_revision = 'bfa43d57de38'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        'tenants',
        'quota_limit',
        existing_type=sa.INTEGER(),
        type_=sa.BigInteger(),
        existing_nullable=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        'tenants',
        'quota_limit',
        existing_type=sa.BigInteger(),
        type_=sa.INTEGER(),
        existing_nullable=False,
    )
    # ### end Alembic commands ###
