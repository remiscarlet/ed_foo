import os

from fastapi import FastAPI

from src.adapters.ingress.cli.router import cli
from src.ingestion.spansh.main import main as ingestion_main

app = None


def main() -> None:
    app_mode = os.getenv("APP_MODE", "ingestion")
    if app_mode == "cli":
        cli()
    elif app_mode == "ingestion":
        ingestion_main()
    else:
        global app
        app = FastAPI()
        # app.include_router(api_router)


if __name__ == "__main__":
    main()
