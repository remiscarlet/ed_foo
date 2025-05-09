drop view if exists derived.unoccupied_systems_view;
create view derived.unoccupied_systems_view as
select
    s.id,
    s.id64,
    s.id_spansh,
    s.id_edsm,
    s.name,
    s.controlling_faction_id,
    s.x,
    s.y,
    s.z,
    s.coords,
    s.date,
    s.allegiance,
    s.population,
    s.primary_economy,
    s.secondary_economy,
    s.security,
    s.government,
    s.body_count,
    s.controlling_power,
    s.power_conflict_progress,
    s.power_state,
    s.power_state_control_progress,
    s.power_state_reinforcement,
    s.power_state_undermining,
    s.powers,
    s.thargoid_war,
    s.controlling_power_updated_at,
    s.power_state_updated_at,
    s.powers_updated_at
from core.systems as s
where s.power_state = 'Unoccupied';
