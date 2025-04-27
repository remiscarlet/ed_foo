# import typer
# from src.adapters.persistence.postgres.system import SystemDB
# from src.core.models import System

# cli = typer.Typer()

# @cli.command()
# def find_high_value(reference_system: str, max_distance: int = 50):
#     system_port = SystemDB()
#     command = FindHighValueSystemsCommand(system_port)
#     systems = command.run(reference_system, max_distance)
#     for system in systems:
#         typer.echo(system)
