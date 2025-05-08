import asyncio
import logging
from functools import wraps
from pprint import pformat
from typing import Annotated, Any, Callable, Coroutine, List

import typer
from tabulate import tabulate

from src.adapters.persistence.postgresql.adapter import (
    ApiCommandAdapter,
    SystemsAdapter,
)
from src.adapters.persistence.postgresql.types import HotspotResult
from src.common.logging import configure_logger
from src.common.utils import get_time_since
from src.ingestion.spansh.pipeline import SpanshDataPipeline


def typer_async[T, **P](f: Callable[P, Coroutine[Any, Any, T]]) -> Callable[P, T]:
    @wraps(f)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        return asyncio.run(f(*args, **kwargs))

    return wrapper


def verbose_count_to_log_level(count: int) -> int:
    match count:
        case 0:
            return logging.INFO
        case 1:
            return logging.DEBUG
        case _:
            return logging.TRACE  # type: ignore # dynamically added


# Debug CLI
debug_cli = typer.Typer()


@debug_cli.command()
def hello_world(name: str) -> None:
    typer.echo(f"Hello World, {name}")


# Data Ingestion CLI
ingestion_cli = typer.Typer()


@ingestion_cli.command()
@typer_async
async def import_spansh(
    verbose: Annotated[int, typer.Option("--verbose", "-v", count=True)] = 0,
    start_at_system_idx: Annotated[
        int, typer.Option("--system-start-idx", "-s", help="System index in the dump to start at.")
    ] = 0,
    skipping_past_every: Annotated[
        int,
        typer.Option(
            "--skipping-past-every", "-S", help="If starting at a non-zero index, print progress every S systems"
        ),
    ] = 1000,
    validated_every: Annotated[
        int, typer.Option("--validated-every", "-V", help="Print json validation progress every V systems")
    ] = 500,
    process_every: Annotated[
        int, typer.Option("--process-every", "-P", help="Batch process and upsert into Postgres every P systems")
    ] = 1500,
    max_market_data_age_days: Annotated[
        int, typer.Option("--max-market-data-age-days", "-M", help="Maximum age of market data to import")
    ] = 30,
) -> None:
    configure_logger(verbose_count_to_log_level(verbose))

    pipeline = SpanshDataPipeline(
        start_at_system_idx=start_at_system_idx,
        skipping_past_every=skipping_past_every,
        validated_every=validated_every,
        process_every=process_every,
        max_market_data_age_days=max_market_data_age_days,
    )
    await pipeline.run()


@ingestion_cli.command()
def download_spansh(
    verbose: Annotated[int, typer.Option("--verbose", "-v", count=True)] = 0,
) -> None:
    configure_logger(verbose_count_to_log_level(verbose))

    SpanshDataPipeline.download_data()


# System CLI
system_cli = typer.Typer()

systems_adapter = SystemsAdapter()


@system_cli.command()
def get_world(world_name: str) -> None:
    system = systems_adapter.get_system(world_name)
    typer.echo(pformat(system))


# API CLI
api_cli = typer.Typer()

api_adapter = ApiCommandAdapter()


def print_hotspot_results(system_name: str, hotspots: List[HotspotResult]) -> None:
    typer.echo("")
    typer.echo("====== SYSTEM ======")
    typer.echo(f"Name: {system_name}")
    typer.echo("")
    if not hotspots:
        typer.echo("!! Found NO hotspots in this system!")

    headers = ["Ring", "Ring Type", "Commodity", "Count"]
    table = []
    for hotspot in hotspots:
        table.append(
            [
                hotspot.ring_name,
                hotspot.ring_type,
                hotspot.commodity,
                hotspot.count,
            ]
        )
    typer.echo(tabulate(table, headers))
    typer.echo("")


@api_cli.command()
def get_hotspots_in_system(system_name: str) -> None:
    hotspots = api_adapter.get_hotspots_in_system(system_name)
    print_hotspot_results(system_name, hotspots)


@api_cli.command()
def get_hotspots_in_system_by_commodities(system_name: str, commodities_filter: List[str]) -> None:
    hotspots = api_adapter.get_hotspots_in_system_by_commodities(system_name, commodities_filter)
    print_hotspot_results(system_name, hotspots)


@api_cli.command()
def get_top_commodities_in_system(
    system_name: str, comms_per_station: int = 5, min_supplydemand: int = 1, is_selling: bool = True
) -> None:
    commodities = api_adapter.get_top_commodities_in_system(
        system_name, comms_per_station, min_supplydemand, is_selling
    )

    typer.echo("")
    typer.echo("====== SYSTEM ======")
    typer.echo(f"Name: {system_name}")
    typer.echo("")
    if not commodities:
        typer.echo("!! Found NO stations with known markets!")

    headers = ["Station Name", "Distance", "Commodity", "Sell Price", "Demand", "Buy Price", "Supply", "Updated Last"]
    table = []
    for commodity in commodities:
        time_since_update = get_time_since(commodity.updated_at) if commodity.updated_at is not None else "Unknown"
        table.append(
            [
                commodity.station_name,
                f"{commodity.distance_to_arrival:.2f} LY",
                commodity.commodity,
                f"{commodity.sell_price} CR",
                commodity.demand,
                f"{commodity.buy_price} CR",
                commodity.supply,
                time_since_update,
            ]
        )
    typer.echo(tabulate(table, headers))
    typer.echo("")


# Main CLI
cli = typer.Typer()

cli.add_typer(ingestion_cli, name="ingestion")
cli.add_typer(debug_cli, name="debug")
cli.add_typer(system_cli, name="system")
cli.add_typer(api_cli, name="api")
