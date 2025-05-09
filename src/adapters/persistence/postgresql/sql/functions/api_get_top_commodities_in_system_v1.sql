drop function if exists api.get_top_commodities_in_system;
create or replace function api.get_top_commodities_in_system(
    p_system_name text,
    p_number_commodities integer,
    p_min_demandsupply integer,
    p_is_selling boolean
)
returns table (
    system_name text,
    station_name text,
    station_type text,
    distance_to_arrival float,
    commodity text,
    sell_price integer,
    demand integer,
    buy_price integer,
    supply integer,
    updated_at timestamp,
    rank bigint
) as $$
declare
    demandsupply_column text := case when p_is_selling then 'demand' else 'supply' end;
    sql text;
begin
    sql := format($f$
        select *
        from (
            select sc.*,
                   dense_rank() over (
                       partition by sc.station_name
                       order by sc.%I desc
                   ) as rank
            from derived.station_commodities_view sc
            where sc.system_name = $2
            and sc.%I >= $3
        ) r
        where r.rank <= $1
    $f$, demandsupply_column, demandsupply_column);

    raise notice 'sql: %', sql;

    return query execute sql
        using p_number_commodities, p_system_name, p_min_demandsupply;
end;
$$ language plpgsql;
