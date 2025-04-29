import typer

from src.adapters.data_ingestion.spansh.downloader import (
    download_spansh_dump as download_spansh_dump_adapter,
)

cli = typer.Typer()


@cli.command()
def download_spansh_dump() -> None:
    download_spansh_dump_adapter()
