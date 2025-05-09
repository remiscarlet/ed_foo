drop function if exists api.get_top_commodities_in_system;
create or replace function api.get_top_commodities_in_system(
    p_system_name text,
    p_number_commodities integer,
    p_min_supplydemand integer,
    p_is_buying boolean
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
    demandsupply_column text := case when p_is_buying then 'supply' else 'demand' end;
    price_column text := case when p_is_buying then 'buy_price' else 'sell_price' end;
    sql text;
begin
    if p_is_buying then
        return query select * from derived.get_top_buy_commodities_in_system(p_system_name, p_number_commodities, p_min_supplydemand);
    else
        return query select * from derived.get_top_sell_commodities_in_system(p_system_name, p_number_commodities, p_min_supplydemand);
    end if;
end;
$$ language plpgsql;
