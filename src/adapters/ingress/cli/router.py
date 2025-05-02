import logging
from pprint import pformat
from typing import Annotated

import typer

from src.adapters.persistence.postgresql.adapter import SystemsAdapter
from src.common.logging import configure_logger
from src.ingestion.spansh.main import SpanshDataPipeline


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
def import_spansh(
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
    ] = 7,
) -> None:
    configure_logger(verbose_count_to_log_level(verbose))

    pipeline = SpanshDataPipeline(
        start_at_system_idx=start_at_system_idx,
        skipping_past_every=skipping_past_every,
        validated_every=validated_every,
        process_every=process_every,
        max_market_data_age_days=max_market_data_age_days,
    )
    pipeline.run()


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


# Main CLI
cli = typer.Typer()

cli.add_typer(ingestion_cli, name="ingestion")
cli.add_typer(debug_cli, name="debug")
cli.add_typer(system_cli, name="system")
