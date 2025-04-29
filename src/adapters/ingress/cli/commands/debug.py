import typer

cli = typer.Typer()


@cli.command()
def hello_world(name: str) -> None:
    typer.echo(f"Hello World, {name}")
