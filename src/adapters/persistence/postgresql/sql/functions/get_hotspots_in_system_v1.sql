drop function if exists api.get_hotspots_in_system;
create or replace function api.get_hotspots_in_system(
    p_system_name TEXT
) returns table (
    body_name TEXT,
    ring_name TEXT,
    ring_type TEXT,
    commodity TEXT,
    count INTEGER
)
as $$
BEGIN
    return query
    select
        h.body_name,
        h.ring_name,
        h.ring_type,
        h.commodity,
        h.count
      from derived.hotspot_ring_view h
	 where h.system_name = p_system_name;
END;
$$ language plpgsql;
