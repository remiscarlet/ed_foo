drop function if exists derived.get_systems_with_power;
create or replace function derived.get_systems_with_power(
    p_power_name text
)
returns table (
    id int,
    id64 bigint,
    id_spansh bigint,
    id_edsm bigint,
    name text,
    controlling_faction_id int,
    x float,
    y float,
    z float,
    coords geometry,
    date timestamp,
    allegiance text,
    population bigint,
    primary_economy text,
    secondary_economy text,
    security text,
    government text,
    body_count int,
    controlling_power text,
    power_conflict_progress jsonb,
    power_state text,
    power_state_control_progress float,
    power_state_reinforcement float,
    power_state_undermining float,
    powers text [],
    thargoid_war jsonb,
    controlling_power_updated_at timestamp,
    power_state_updated_at timestamp,
    powers_updated_at timestamp
) as $$
    select
        s.id, s.id64, s.id_spansh, s.id_edsm, s.name,
        s.controlling_faction_id, s.x, s.y, s.z, s.coords, s.date,
        s.allegiance, s.population, s.primary_economy,
        s.secondary_economy, s.security, s.government,
        s.body_count, s.controlling_power, s.power_conflict_progress,
        s.power_state, s.power_state_control_progress,
        s.power_state_reinforcement, s.power_state_undermining,
        s.powers, s.thargoid_war, s.controlling_power_updated_at,
        s.power_state_updated_at, s.powers_updated_at
    from core.systems s
    where s.controlling_power = p_power_name;
$$ language sql;
