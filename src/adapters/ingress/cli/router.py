from pprint import pformat

import typer

from src.adapters.persistence.postgresql.adapter import SystemsAdapter

# Debug CLI
debug_cli = typer.Typer()


@debug_cli.command()
def hello_world(name: str) -> None:
    typer.echo(f"Hello World, {name}")


# System CLI
system_cli = typer.Typer()

systems_adapter = SystemsAdapter()


@system_cli.command()
def get_world(world_name: str) -> None:
    system = systems_adapter.get_system(world_name)
    typer.echo(pformat(system))


# Main CLI
cli = typer.Typer()

cli.add_typer(debug_cli, name="debug")
cli.add_typer(system_cli, name="system")
