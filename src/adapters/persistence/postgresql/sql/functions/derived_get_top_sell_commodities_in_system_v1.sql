drop function if exists derived.get_top_sell_commodities_in_system;
create or replace function derived.get_top_sell_commodities_in_system(
    p_system_name text,
    p_number_commodities integer,
    p_min_demand integer
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
    select *
    from (
        select sc.*,
                dense_rank() over (
                    partition by sc.station_name
                    order by derived.calculate_commodity_score(sc.sell_price, sc.demand) desc
                ) as rank
        from derived.station_commodities_view sc
        where sc.system_name = p_system_name
        and sc.demand >= p_min_demand
    ) r
    where r.rank <= p_number_commodities
$$ language sql;
