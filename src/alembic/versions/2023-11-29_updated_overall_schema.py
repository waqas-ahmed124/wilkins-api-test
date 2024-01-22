"""updated overall schema

Revision ID: 2f362a292336
Revises: aefc31a79080
Create Date: 2023-11-29 14:48:00.347265

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from apiserver.models import ProjectStatusEnum

# revision identifiers, used by Alembic.
revision: str = '2f362a292336'
down_revision: Union[str, None] = 'aefc31a79080'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_submission_id', table_name='submission')
    op.drop_table('submission')
    op.drop_index('ix_project_id', table_name='project')
    op.drop_index('ix_project_wilkins_id', table_name='project')
    op.drop_table('project')

    project_status_enum = postgresql.ENUM(
        ProjectStatusEnum,
        name='project_status_enum'
    )
    project_status_enum.drop(op.get_bind())

    op.create_table('projects',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('wilkins_id', sa.String(length=256), nullable=True),
    sa.Column('name', sa.String(length=256), nullable=True),
    sa.Column('client', sa.String(length=256), nullable=True),
    sa.Column('status', sa.Enum('active', 'delivered', 'vendor_request_sent', 'closed', 'sold', 'lost', 'not_started', name='project_status_enum'), nullable=False),
    sa.Column('budget', sa.Float(), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_projects_id'), 'projects', ['id'], unique=False)
    op.create_index(op.f('ix_projects_wilkins_id'), 'projects', ['wilkins_id'], unique=True)
    op.create_table('vendors',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.Column('emails', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_vendors_id'), 'vendors', ['id'], unique=False)
    op.create_table('project_vendors',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('project_id', sa.Integer(), nullable=False),
    sa.Column('vendor_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_project_vendors_id'), 'project_vendors', ['id'], unique=False)
    op.create_table('submissions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('unit', sa.String(length=256), nullable=False),
    sa.Column('project_id', sa.Integer(), nullable=False),
    sa.Column('vendor_id', sa.Integer(), nullable=False),
    sa.Column('town', sa.String(length=256), nullable=True),
    sa.Column('market', sa.String(length=256), nullable=True),
    sa.Column('state', sa.String(length=256), nullable=True),
    sa.Column('location_description', sa.Text(), nullable=True),
    sa.Column('geopath_id', sa.String(length=512), nullable=True),
    sa.Column('target_location', sa.String(length=512), nullable=True),
    sa.Column('distance_to_location', sa.Float(), nullable=True),
    sa.Column('a18_weekly_impressions', sa.Integer(), nullable=True),
    sa.Column('a18_4wk_reach', sa.Float(), nullable=True),
    sa.Column('a18_4wk_freq', sa.Float(), nullable=True),
    sa.Column('media_type', sa.String(length=64), nullable=True),
    sa.Column('facing', sa.String(length=16), nullable=True),
    sa.Column('is_illuminated', sa.Boolean(), nullable=False),
    sa.Column('availability_start', sa.Date(), nullable=True),
    sa.Column('availability_end', sa.Date(), nullable=True),
    sa.Column('total_units', sa.Integer(), nullable=True),
    sa.Column('installation_cost', sa.Float(), nullable=True),
    sa.Column('four_week_media_cost', sa.Float(), nullable=True),
    sa.Column('markup_percentage', sa.Float(), nullable=True),
    sa.Column('production_cost', sa.Float(), nullable=True),
    sa.Column('is_prod_forced', sa.Boolean(), nullable=False),
    sa.Column('taxes', sa.Float(), nullable=True),
    sa.Column('four_week_rate_card', sa.Float(), nullable=True),
    sa.Column('internal_four_week_media_cost', sa.Float(), nullable=True),
    sa.Column('additional_installation_cost', sa.Float(), nullable=True),
    sa.Column('initial_installation_cost', sa.Float(), nullable=True),
    sa.Column('unit_highlights', sa.String(length=256), nullable=True),
    sa.Column('latitude', sa.Float(), nullable=True),
    sa.Column('longitude', sa.Float(), nullable=True),
    sa.Column('no_of_spots_per_loop', sa.Float(), nullable=True),
    sa.Column('spot_length_secs', sa.Float(), nullable=True),
    sa.Column('user_locked', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('unit')
    )
    op.create_index(op.f('ix_submissions_id'), 'submissions', ['id'], unique=False)
    op.create_table('user_projects',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('project_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_projects_id'), 'user_projects', ['id'], unique=False)
    op.add_column('users', sa.Column('name', sa.String(length=64), nullable=True))
    op.execute("UPDATE users SET name='please_update_username' WHERE name IS NULL;")
    op.alter_column('users', 'name', nullable=False)
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='false'))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'is_admin')
    op.drop_column('users', 'name')
    op.create_table('project',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('project_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('wilkins_id', sa.VARCHAR(length=256), autoincrement=False, nullable=True),
    sa.Column('name', sa.VARCHAR(length=256), autoincrement=False, nullable=True),
    sa.Column('client', sa.VARCHAR(length=256), autoincrement=False, nullable=True),
    sa.Column('status', postgresql.ENUM('active', 'delivered', 'vendor_request_sent', 'closed', 'sold', 'lost', 'not_started', name='project_status_enum'), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='project_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_index('ix_project_wilkins_id', 'project', ['wilkins_id'], unique=False)
    op.create_index('ix_project_id', 'project', ['id'], unique=False)
    op.create_table('submission',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('vendor', sa.VARCHAR(length=256), autoincrement=False, nullable=False),
    sa.Column('unit', sa.VARCHAR(length=256), autoincrement=False, nullable=False),
    sa.Column('project_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.Column('city', sa.VARCHAR(length=256), autoincrement=False, nullable=False),
    sa.Column('state', sa.VARCHAR(length=256), autoincrement=False, nullable=False),
    sa.Column('location', sa.VARCHAR(length=256), autoincrement=False, nullable=False),
    sa.Column('location_description', sa.VARCHAR(length=256), autoincrement=False, nullable=True),
    sa.Column('size', sa.VARCHAR(length=64), autoincrement=False, nullable=False),
    sa.Column('media_type', sa.VARCHAR(length=64), autoincrement=False, nullable=False),
    sa.Column('facing', sa.VARCHAR(length=16), autoincrement=False, nullable=False),
    sa.Column('availability', sa.VARCHAR(length=256), autoincrement=False, nullable=False),
    sa.Column('is_illuminated', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('four_week_media_cost', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('a24_49_weekly_expressions', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('a18_weekly_expressions', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('a18_reach', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('a18_freq', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('initial_installation_cost', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('production_cost', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('latitude', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('longitude', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('no_of_spots', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('spot_length', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['project_id'], ['project.id'], name='submission_project_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='submission_pkey')
    )
    op.create_index('ix_submission_id', 'submission', ['id'], unique=False)
    op.drop_index(op.f('ix_user_projects_id'), table_name='user_projects')
    op.drop_table('user_projects')
    op.drop_index(op.f('ix_submissions_id'), table_name='submissions')
    op.drop_table('submissions')
    op.drop_index(op.f('ix_project_vendors_id'), table_name='project_vendors')
    op.drop_table('project_vendors')
    op.drop_index(op.f('ix_vendors_id'), table_name='vendors')
    op.drop_table('vendors')
    op.drop_index(op.f('ix_projects_wilkins_id'), table_name='projects')
    op.drop_index(op.f('ix_projects_id'), table_name='projects')
    op.drop_table('projects')
    # ### end Alembic commands ###
