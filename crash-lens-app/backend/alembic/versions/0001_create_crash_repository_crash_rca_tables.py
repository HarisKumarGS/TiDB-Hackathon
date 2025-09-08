"""Create crash, repository, and crash_rca tables

Revision ID: 0001
Revises: 
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create repository table
    op.create_table('repository',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create crash table
    op.create_table('crash',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('component', sa.String(length=255), nullable=False),
        sa.Column('error_type', sa.String(length=255), nullable=False),
        sa.Column('severity', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('impacted_users', sa.Integer(), nullable=False),
        sa.Column('comment', sa.String(length=500), nullable=True),
        sa.Column('repository_id', sa.String(), nullable=False),
        sa.Column('error_log', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['repository_id'], ['repository.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create crash_rca table
    op.create_table('crash_rca',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('crash_id', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('problem_identification', sa.Text(), nullable=True),
        sa.Column('data_collection', sa.Text(), nullable=True),
        sa.Column('analysis', sa.Text(), nullable=True),
        sa.Column('root_cause_identification', sa.Text(), nullable=True),
        sa.Column('solution', sa.Text(), nullable=True),
        sa.Column('author', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('supporting_documents', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['crash_id'], ['crash.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for better performance
    op.create_index('ix_crash_repository_id', 'crash', ['repository_id'])
    op.create_index('ix_crash_severity', 'crash', ['severity'])
    op.create_index('ix_crash_status', 'crash', ['status'])
    op.create_index('ix_crash_created_at', 'crash', ['created_at'])
    op.create_index('ix_crash_rca_crash_id', 'crash_rca', ['crash_id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_crash_rca_crash_id', table_name='crash_rca')
    op.drop_index('ix_crash_created_at', table_name='crash')
    op.drop_index('ix_crash_status', table_name='crash')
    op.drop_index('ix_crash_severity', table_name='crash')
    op.drop_index('ix_crash_repository_id', table_name='crash')
    
    # Drop tables in reverse order
    op.drop_table('crash_rca')
    op.drop_table('crash')
    op.drop_table('repository')
