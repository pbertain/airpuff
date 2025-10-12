"""Initial database schema

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create airports table
    op.create_table('airports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('icao', sa.String(length=4), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('latitude', sa.Numeric(precision=9, scale=6), nullable=True),
        sa.Column('longitude', sa.Numeric(precision=9, scale=6), nullable=True),
        sa.Column('elevation_ft', sa.Integer(), nullable=True),
        sa.Column('atis_phone', sa.String(length=20), nullable=True),
        sa.Column('tower_phone', sa.String(length=20), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('state', sa.String(length=50), nullable=True),
        sa.Column('country', sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_airports_id'), 'airports', ['id'], unique=False)
    op.create_index(op.f('ix_airports_icao'), 'airports', ['icao'], unique=True)

    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('avatar_url', sa.String(length=500), nullable=True),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('provider_id', sa.String(length=255), nullable=False),
        sa.Column('units', sa.String(length=10), nullable=True),
        sa.Column('default_airports', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('last_login', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('api_key', sa.String(length=64), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_api_key'), 'users', ['api_key'], unique=True)

    # Create routes table
    op.create_table('routes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('is_public', sa.Boolean(), nullable=True),
        sa.Column('is_favorite', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_routes_id'), 'routes', ['id'], unique=False)

    # Create weather_observations table
    op.create_table('weather_observations',
        sa.Column('time', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('airport_id', sa.Integer(), nullable=False),
        sa.Column('temperature_f', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('temperature_c', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('dewpoint_f', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('dewpoint_c', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('temp_dewpoint_spread_f', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('wind_dir_deg', sa.Integer(), nullable=True),
        sa.Column('wind_speed_kts', sa.Integer(), nullable=True),
        sa.Column('wind_speed_mph', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('wind_gust_kts', sa.Integer(), nullable=True),
        sa.Column('visibility_mi', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('visibility_m', sa.Numeric(precision=7, scale=2), nullable=True),
        sa.Column('ceiling_ft', sa.Integer(), nullable=True),
        sa.Column('ceiling_code', sa.String(length=10), nullable=True),
        sa.Column('altimeter_hg', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('altimeter_mb', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column('flight_category', sa.String(length=10), nullable=True),
        sa.Column('raw_metar', sa.Text(), nullable=True),
        sa.Column('metar_type', sa.String(length=10), nullable=True),
        sa.Column('auto_station', sa.String(length=10), nullable=True),
        sa.Column('wind_chill_f', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('heat_index_f', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.ForeignKeyConstraint(['airport_id'], ['airports.id'], ),
        sa.PrimaryKeyConstraint('time', 'airport_id')
    )

    # Create route_airports association table
    op.create_table('route_airports',
        sa.Column('route_id', sa.Integer(), nullable=False),
        sa.Column('airport_id', sa.Integer(), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['airport_id'], ['airports.id'], ),
        sa.ForeignKeyConstraint(['route_id'], ['routes.id'], ),
        sa.PrimaryKeyConstraint('route_id', 'airport_id')
    )

    # Create route_airport_details table
    op.create_table('route_airport_details',
        sa.Column('route_id', sa.Integer(), nullable=False),
        sa.Column('airport_id', sa.Integer(), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_waypoint', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['airport_id'], ['airports.id'], ),
        sa.ForeignKeyConstraint(['route_id'], ['routes.id'], ),
        sa.PrimaryKeyConstraint('route_id', 'airport_id')
    )

    # Create scheduled_messages table
    op.create_table('scheduled_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('route_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('message_type', sa.String(length=20), nullable=False),
        sa.Column('phone_number', sa.String(length=20), nullable=False),
        sa.Column('schedule_type', sa.String(length=20), nullable=False),
        sa.Column('schedule_time', sa.String(length=10), nullable=True),
        sa.Column('schedule_days', sa.String(length=20), nullable=True),
        sa.Column('message_template', sa.Text(), nullable=True),
        sa.Column('include_forecast', sa.Boolean(), nullable=True),
        sa.Column('max_airports', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('last_sent', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('next_send', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['route_id'], ['routes.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scheduled_messages_id'), 'scheduled_messages', ['id'], unique=False)

    # Create TimescaleDB hypertable (only for PostgreSQL with TimescaleDB extension)
    # For SQLite, we'll skip this step
    # op.execute("SELECT create_hypertable('weather_observations', 'time', if_not_exists => TRUE);")


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('scheduled_messages')
    op.drop_table('route_airport_details')
    op.drop_table('route_airports')
    op.drop_table('weather_observations')
    op.drop_table('routes')
    op.drop_table('users')
    op.drop_table('airports')
