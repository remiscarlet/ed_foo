-- Gets fortified and stronghold systems in range of `p_system_name`
-- that can expand into current unoccupied system
drop function if exists api.get_expandable_systems_in_range;
create or replace function api.get_expandable_systems_in_range(
    p_system_name TEXT
)
returns table (
    id INT,
    id64 BIGINT,
    id_spansh BIGINT,
    id_edsm BIGINT,
    name TEXT,
    controlling_faction_id INT,
    x FLOAT,
    y FLOAT,
    z FLOAT,
    coords GEOMETRY,
    date TIMESTAMP,
    allegiance TEXT,
    population BIGINT,
    primary_economy TEXT,
    secondary_economy TEXT,
    security TEXT,
    government TEXT,
    body_count INT,
    controlling_power TEXT,
    power_conflict_progress JSONB,
    power_state TEXT,
    power_state_control_progress FLOAT,
    power_state_reinforcement FLOAT,
    power_state_undermining FLOAT,
    powers TEXT [],
    thargoid_war JSONB,
    controlling_power_updated_at TIMESTAMP,
    power_state_updated_at TIMESTAMP,
    powers_updated_at TIMESTAMP
) as $$
BEGIN
    return query
    select
        s.id, s.id64, s.id_spansh, s.id_edsm, s.name,
        s.controlling_faction_id, s.x, s.y, s.z, s.coords,
        s.date, s.allegiance, s.population, s.primary_economy,
        s.secondary_economy, s.security, s.government,
        s.body_count, s.controlling_power, s.power_conflict_progress,
        s.power_state, s.power_state_control_progress,
        s.power_state_reinforcement, s.power_state_undermining,
        s.powers, s.thargoid_war, s.controlling_power_updated_at,
        s.power_state_updated_at, s.powers_updated_at
    from derived.get_systems_with_power_and_state(
        'Nakato Kaine',
        array['Stronghold', 'Fortified']
    ) s
    where ST_3DDWithin(
        s.coords,
        (select s.coords from core.systems s where s.name = p_system_name),
        case when s.power_state = 'Stronghold' then 30 else 20 end
    );
END;
$$ language plpgsql;
