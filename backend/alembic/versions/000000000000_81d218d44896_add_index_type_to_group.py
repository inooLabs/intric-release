"""add index type to group
Revision ID: 81d218d44896
Revises: 9ce1be90c179
Create Date: 2024-03-08 16:47:43.642055
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic
revision = '81d218d44896'
down_revision = '9ce1be90c179'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('groups', sa.Column('index_type', sa.String(), nullable=True))

    conn = op.get_bind()
    conn.execute(
        sa.text("UPDATE groups SET index_type = :index_type"),
        parameters={"index_type": "hnsw"},
    )

    op.alter_column('groups', 'index_type', nullable=False)

    op.alter_column('groups', 'user_id', existing_type=sa.INTEGER(), nullable=False)
    op.alter_column(
        'groups',
        'name',
        existing_type=sa.TEXT(),
        type_=sa.String(),
        existing_nullable=False,
    )
    op.alter_column(
        'groups',
        'embedding_model',
        existing_type=sa.TEXT(),
        type_=sa.String(),
        nullable=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        'groups',
        'embedding_model',
        existing_type=sa.String(),
        type_=sa.TEXT(),
        nullable=True,
    )
    op.alter_column(
        'groups',
        'name',
        existing_type=sa.String(),
        type_=sa.TEXT(),
        existing_nullable=False,
    )
    op.alter_column('groups', 'user_id', existing_type=sa.INTEGER(), nullable=True)
    op.drop_column('groups', 'index_type')
    # ### end Alembic commands ###
