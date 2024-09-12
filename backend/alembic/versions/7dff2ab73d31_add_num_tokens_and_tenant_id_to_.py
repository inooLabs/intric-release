"""add num tokens and tenant id to questions
Revision ID: 7dff2ab73d31
Revises: 34920d3f8a4d
Create Date: 2024-08-20 10:51:14.740959
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic
revision = '7dff2ab73d31'
down_revision = '34920d3f8a4d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        'questions', sa.Column('num_tokens_question', sa.Integer(), nullable=True)
    )
    op.add_column(
        'questions', sa.Column('num_tokens_answer', sa.Integer(), nullable=True)
    )
    op.add_column('questions', sa.Column('tenant_id', sa.UUID(), nullable=True))
    op.create_index(
        op.f('ix_questions_tenant_id'), 'questions', ['tenant_id'], unique=False
    )
    op.create_foreign_key(
        'questions_tenants_fkey',
        'questions',
        'tenants',
        ['tenant_id'],
        ['id'],
        ondelete='CASCADE',
    )

    # Set all old tokens numbers to zero
    op.execute(
        sa.text("UPDATE questions SET num_tokens_question = 0, num_tokens_answer = 0")
    )

    # Set tenant id
    op.execute(
        sa.text(
            "UPDATE public.questions q "
            "SET tenant_id = COALESCE("
            "    (SELECT u.tenant_id FROM public.users u "
            "     JOIN public.services s ON s.id = q.service_id "
            "     WHERE s.user_id = u.id), "
            "    (SELECT u.tenant_id FROM public.users u "
            "     JOIN public.sessions sess ON sess.id = q.session_id "
            "     WHERE sess.user_id = u.id)"
            ") "
            "WHERE q.service_id IS NOT NULL OR q.session_id IS NOT NULL;"
        )
    )

    op.alter_column('questions', 'num_tokens_question', nullable=False)
    op.alter_column('questions', 'num_tokens_answer', nullable=False)
    op.alter_column('questions', 'tenant_id', nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('questions_tenants_fkey', 'questions', type_='foreignkey')
    op.drop_index(op.f('ix_questions_tenant_id'), table_name='questions')
    op.drop_column('questions', 'tenant_id')
    op.drop_column('questions', 'num_tokens_answer')
    op.drop_column('questions', 'num_tokens_question')
    # ### end Alembic commands ###
