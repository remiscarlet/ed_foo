"""Create initial tables

Revision ID: 6b82a9368504
Revises:
Create Date: 2025-05-06 23:21:18.360145

"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op
from geoalchemy2 import Geometry
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "6b82a9368504"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    op.execute("CREATE SCHEMA IF NOT EXISTS core")
    op.execute("CREATE SCHEMA IF NOT EXISTS derived")
    op.execute("CREATE SCHEMA IF NOT EXISTS api")
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "commodities",
        sa.Column("id64", sa.BigInteger(), nullable=True),
        sa.Column("symbol", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("avg_price", sa.Integer(), nullable=True),
        sa.Column("rare_goods", sa.Boolean(), nullable=True),
        sa.Column("corrosive", sa.Boolean(), nullable=True),
        sa.Column("category", sa.Text(), nullable=True),
        sa.Column("is_mineable", sa.Boolean(), nullable=True),
        sa.Column("ring_types", sa.ARRAY(sa.Text()), nullable=True),
        sa.Column("mining_method", sa.Text(), nullable=True),
        sa.Column("has_hotspots", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("symbol"),
        schema="core",
    )
    op.create_table(
        "factions",
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("allegiance", sa.Text(), nullable=True),
        sa.Column("government", sa.Text(), nullable=True),
        sa.Column("is_player", sa.Boolean(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        schema="core",
    )
    op.create_table(
        "ship_modules",
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("module_id", sa.Integer(), nullable=True),
        sa.Column("symbol", sa.Text(), nullable=False),
        sa.Column("category", sa.Text(), nullable=True),
        sa.Column("rating", sa.Text(), nullable=True),
        sa.Column("ship", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("name"),
        schema="core",
    )
    op.create_table(
        "ships",
        sa.Column("symbol", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("ship_id", sa.Integer(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("symbol"),
        schema="core",
    )
    op.create_table(
        "stations",
        sa.Column("id64", sa.BigInteger(), nullable=True),
        sa.Column("id_spansh", sa.BigInteger(), nullable=True),
        sa.Column("id_edsm", sa.BigInteger(), nullable=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("owner_type", sa.Text(), nullable=False),
        sa.Column("allegiance", sa.Text(), nullable=True),
        sa.Column("controlling_faction", sa.Text(), nullable=True),
        sa.Column("controlling_faction_state", sa.Text(), nullable=True),
        sa.Column("distance_to_arrival", sa.Float(), nullable=True),
        sa.Column("economies", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("government", sa.Text(), nullable=True),
        sa.Column("large_landing_pads", sa.Integer(), nullable=True),
        sa.Column("medium_landing_pads", sa.Integer(), nullable=True),
        sa.Column("small_landing_pads", sa.Integer(), nullable=True),
        sa.Column("primary_economy", sa.Text(), nullable=True),
        sa.Column("services", sa.ARRAY(sa.Text()), nullable=True),
        sa.Column("type", sa.Text(), nullable=True),
        sa.Column("prohibited_commodities", sa.ARRAY(sa.Text()), nullable=True),
        sa.Column("carrier_name", sa.Text(), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("spansh_updated_at", sa.DateTime(), nullable=True),
        sa.Column("edsm_updated_at", sa.DateTime(), nullable=True),
        sa.Column("eddn_updated_at", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", "owner_id", name="_station_name_owner_distanace_uc"),
        schema="core",
    )
    op.create_index(op.f("ix_core_stations_name"), "stations", ["name"], unique=False, schema="core")
    op.create_index(op.f("ix_core_stations_owner_id"), "stations", ["owner_id"], unique=False, schema="core")
    op.create_index(op.f("ix_core_stations_owner_type"), "stations", ["owner_type"], unique=False, schema="core")
    op.create_table(
        "market_commodities",
        sa.Column("station_id", sa.Integer(), nullable=False),
        sa.Column("commodity_sym", sa.Text(), nullable=False),
        sa.Column("buy_price", sa.Integer(), nullable=True),
        sa.Column("sell_price", sa.Integer(), nullable=True),
        sa.Column("supply", sa.Integer(), nullable=True),
        sa.Column("demand", sa.Integer(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["commodity_sym"],
            ["core.commodities.symbol"],
        ),
        sa.ForeignKeyConstraint(
            ["station_id"],
            ["core.stations.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("station_id", "commodity_sym", name="_station_market_commodity_uc"),
        schema="core",
    )
    op.create_index(
        op.f("ix_core_market_commodities_station_id"), "market_commodities", ["station_id"], unique=False, schema="core"
    )
    op.create_table(
        "outfitting_ship_modules",
        sa.Column("station_id", sa.Integer(), nullable=False),
        sa.Column("module_name", sa.Text(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["module_name"],
            ["core.ship_modules.name"],
        ),
        sa.ForeignKeyConstraint(
            ["station_id"],
            ["core.stations.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("station_id", "module_name", name="_station_outfitting_module_uc"),
        schema="core",
    )
    op.create_index(
        op.f("ix_core_outfitting_ship_modules_station_id"),
        "outfitting_ship_modules",
        ["station_id"],
        unique=False,
        schema="core",
    )
    op.create_table(
        "shipyard_ships",
        sa.Column("station_id", sa.Integer(), nullable=False),
        sa.Column("ship_sym", sa.Text(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["ship_sym"],
            ["core.ships.symbol"],
        ),
        sa.ForeignKeyConstraint(
            ["station_id"],
            ["core.stations.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("station_id", "ship_sym", name="_station_shipyard_ship_uc"),
        schema="core",
    )
    op.create_index(
        op.f("ix_core_shipyard_ships_station_id"), "shipyard_ships", ["station_id"], unique=False, schema="core"
    )
    op.create_table(
        "systems",
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("id64", sa.BigInteger(), nullable=True),
        sa.Column("id_spansh", sa.BigInteger(), nullable=True),
        sa.Column("id_edsm", sa.BigInteger(), nullable=True),
        sa.Column("x", sa.Float(), nullable=False),
        sa.Column("y", sa.Float(), nullable=False),
        sa.Column("z", sa.Float(), nullable=False),
        sa.Column(
            "coords",
            Geometry(geometry_type="POINTZ", srid=0, from_text="ST_GeomFromEWKT", name="geometry"),
            nullable=False,
        ),
        sa.Column("date", sa.DateTime(), nullable=True),
        sa.Column("allegiance", sa.Text(), nullable=True),
        sa.Column("population", sa.BigInteger(), nullable=True),
        sa.Column("primary_economy", sa.Text(), nullable=True),
        sa.Column("secondary_economy", sa.Text(), nullable=True),
        sa.Column("security", sa.Text(), nullable=True),
        sa.Column("government", sa.Text(), nullable=True),
        sa.Column("body_count", sa.Integer(), nullable=True),
        sa.Column("controlling_power", sa.Text(), nullable=True),
        sa.Column("power_conflict_progress", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("power_state", sa.Text(), nullable=True),
        sa.Column("power_state_control_progress", sa.Float(), nullable=True),
        sa.Column("power_state_reinforcement", sa.Float(), nullable=True),
        sa.Column("power_state_undermining", sa.Float(), nullable=True),
        sa.Column("powers", sa.ARRAY(sa.Text()), nullable=True),
        sa.Column("thargoid_war", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("controlling_power_updated_at", sa.DateTime(), nullable=True),
        sa.Column("power_state_updated_at", sa.DateTime(), nullable=True),
        sa.Column("powers_updated_at", sa.DateTime(), nullable=True),
        sa.Column("controlling_faction_id", sa.Integer(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["controlling_faction_id"],
            ["core.factions.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        schema="core",
    )
    op.create_index(
        op.f("ix_core_systems_controlling_faction_id"),
        "systems",
        ["controlling_faction_id"],
        unique=False,
        schema="core",
    )
    op.create_table(
        "bodies",
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("id64", sa.BigInteger(), nullable=True),
        sa.Column("id_spansh", sa.BigInteger(), nullable=True),
        sa.Column("id_edsm", sa.BigInteger(), nullable=True),
        sa.Column("body_id", sa.Integer(), nullable=True),
        sa.Column("system_id", sa.Integer(), nullable=False),
        sa.Column("atmosphere_composition", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("materials", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("parents", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("absolute_magnitude", sa.Float(), nullable=True),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("arg_of_periapsis", sa.Float(), nullable=True),
        sa.Column("ascending_node", sa.Float(), nullable=True),
        sa.Column("atmosphere_type", sa.Text(), nullable=True),
        sa.Column("axial_tilt", sa.Float(), nullable=True),
        sa.Column("distance_to_arrival", sa.Float(), nullable=True),
        sa.Column("earth_masses", sa.Float(), nullable=True),
        sa.Column("gravity", sa.Float(), nullable=True),
        sa.Column("is_landable", sa.Boolean(), nullable=True),
        sa.Column("luminosity", sa.Text(), nullable=True),
        sa.Column("main_star", sa.Boolean(), nullable=True),
        sa.Column("mean_anomaly", sa.Float(), nullable=True),
        sa.Column("orbital_eccentricity", sa.Float(), nullable=True),
        sa.Column("orbital_inclination", sa.Float(), nullable=True),
        sa.Column("orbital_period", sa.Float(), nullable=True),
        sa.Column("radius", sa.Float(), nullable=True),
        sa.Column("reserve_level", sa.Text(), nullable=True),
        sa.Column("rotational_period", sa.Float(), nullable=True),
        sa.Column("rotational_period_tidally_locked", sa.Boolean(), nullable=True),
        sa.Column("semi_major_axis", sa.Float(), nullable=True),
        sa.Column("solar_masses", sa.Float(), nullable=True),
        sa.Column("solar_radius", sa.Float(), nullable=True),
        sa.Column("solid_composition", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("spectral_class", sa.Text(), nullable=True),
        sa.Column("sub_type", sa.Text(), nullable=True),
        sa.Column("surface_pressure", sa.Float(), nullable=True),
        sa.Column("surface_temperature", sa.Float(), nullable=True),
        sa.Column("terraforming_state", sa.Text(), nullable=True),
        sa.Column("type", sa.Text(), nullable=True),
        sa.Column("volcanism_type", sa.Text(), nullable=True),
        sa.Column("mean_anomaly_updated_at", sa.DateTime(), nullable=True),
        sa.Column("distance_to_arrival_updated_at", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["system_id"],
            ["core.systems.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("system_id", "name", "body_id", name="_bodies_uc"),
        schema="core",
    )
    op.create_index(op.f("ix_core_bodies_system_id"), "bodies", ["system_id"], unique=False, schema="core")
    op.create_table(
        "faction_presences",
        sa.Column("system_id", sa.Integer(), nullable=False),
        sa.Column("faction_id", sa.Integer(), nullable=False),
        sa.Column("influence", sa.Float(), nullable=True),
        sa.Column("state", sa.Text(), nullable=True),
        sa.Column("happiness", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("active_states", sa.ARRAY(sa.Text()), nullable=True),
        sa.Column("pending_states", sa.ARRAY(sa.Text()), nullable=True),
        sa.Column("recovering_states", sa.ARRAY(sa.Text()), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["faction_id"],
            ["core.factions.id"],
        ),
        sa.ForeignKeyConstraint(
            ["system_id"],
            ["core.systems.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("system_id", "faction_id", name="_system_faction_presence_uc"),
        schema="core",
    )
    op.create_index(
        op.f("ix_core_faction_presences_faction_id"), "faction_presences", ["faction_id"], unique=False, schema="core"
    )
    op.create_index(
        op.f("ix_core_faction_presences_system_id"), "faction_presences", ["system_id"], unique=False, schema="core"
    )
    op.create_table(
        "thargoid_wars",
        sa.Column("system_id", sa.Integer(), nullable=False),
        sa.Column("current_state", sa.Text(), nullable=False),
        sa.Column("days_remaining", sa.Float(), nullable=False),
        sa.Column("failure_state", sa.Text(), nullable=False),
        sa.Column("ports_remaining", sa.Float(), nullable=False),
        sa.Column("progress", sa.Float(), nullable=False),
        sa.Column("success_reached", sa.Boolean(), nullable=False),
        sa.Column("success_state", sa.Text(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["system_id"],
            ["core.systems.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="core",
    )
    op.create_index(
        op.f("ix_core_thargoid_wars_system_id"), "thargoid_wars", ["system_id"], unique=False, schema="core"
    )
    op.create_table(
        "rings",
        sa.Column("id64", sa.BigInteger(), nullable=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("body_id", sa.Integer(), nullable=False),
        sa.Column("type", sa.Text(), nullable=True),
        sa.Column("mass", sa.Float(), nullable=True),
        sa.Column("inner_radius", sa.Float(), nullable=True),
        sa.Column("outer_radius", sa.Float(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["body_id"],
            ["core.bodies.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("body_id", "name", name="_ring_on_body_uc"),
        schema="core",
    )
    op.create_index(op.f("ix_core_rings_body_id"), "rings", ["body_id"], unique=False, schema="core")
    op.create_table(
        "signals",
        sa.Column("body_id", sa.Integer(), nullable=False),
        sa.Column("signal_type", sa.Text(), nullable=True),
        sa.Column("count", sa.Integer(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["body_id"],
            ["core.bodies.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("body_id", "signal_type", name="_signal_on_body_uc"),
        schema="core",
    )
    op.create_index(op.f("ix_core_signals_body_id"), "signals", ["body_id"], unique=False, schema="core")
    op.create_table(
        "hotspots",
        sa.Column("ring_id", sa.Integer(), nullable=False),
        sa.Column("commodity_sym", sa.Text(), nullable=False),
        sa.Column("count", sa.Integer(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["commodity_sym"],
            ["core.commodities.symbol"],
        ),
        sa.ForeignKeyConstraint(
            ["ring_id"],
            ["core.rings.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ring_id", "commodity_sym", name="_ring_and_commodity_uc"),
        schema="core",
    )
    op.create_index(op.f("ix_core_hotspots_ring_id"), "hotspots", ["ring_id"], unique=False, schema="core")
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP SCHEMA IF EXISTS core CASCADE")
    op.execute("DROP SCHEMA IF EXISTS derived CASCADE")
    op.execute("DROP SCHEMA IF EXISTS api CASCADE")
    op.execute("DROP EXTENSION IF EXISTS postgis")
