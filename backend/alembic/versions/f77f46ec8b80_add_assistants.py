"""add_assistants
Revision ID: f77f46ec8b80
Revises: 2b9ef0edd2fc
Create Date: 2023-10-17 08:45:24.059399
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic
revision = 'f77f46ec8b80'
down_revision = '2b9ef0edd2fc'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'assistants',
        sa.Column(
            'created_at',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.Column(
            'updated_at',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column(
            'uuid',
            postgresql.UUID(as_uuid=True),
            server_default=sa.text('gen_random_uuid()'),
            nullable=False,
        ),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('prompt', sa.Text(), nullable=False),
        sa.Column('completion_model', sa.Text(), nullable=False),
        sa.Column(
            'completion_model_kwargs',
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column('embedding_model', sa.Text(), nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ['group_id'],
            ['groups.id'],
        ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_assistants_id'), 'assistants', ['id'], unique=False)
    op.create_index(op.f('ix_assistants_uuid'), 'assistants', ['uuid'], unique=False)
    op.add_column('sessions', sa.Column('assistant_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        "sessions_assistants_fkey",
        'sessions',
        'assistants',
        ['assistant_id'],
        ['id'],
        ondelete='CASCADE',
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("sessions_assistants_fkey", 'sessions', type_='foreignkey')
    op.drop_column('sessions', 'assistant_id')
    op.drop_index(op.f('ix_assistants_uuid'), table_name='assistants')
    op.drop_index(op.f('ix_assistants_id'), table_name='assistants')
    op.drop_table('assistants')
    # ### end Alembic commands ###
