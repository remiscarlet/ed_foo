import typer

from src.adapters.ingress.cli.commands import data, debug

cli = typer.Typer()

cli.add_typer(data.cli, name="data")
cli.add_typer(debug.cli, name="debug")

# cli.add_typer(users.cli, name="users")
# cli.add_typer(systems.cli, name="systems")

if __name__ == "__main__":
    cli()
