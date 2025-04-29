import os

from fastapi import FastAPI

from src.adapters.ingress.cli.router import cli

app = None


def main() -> None:
    app_mode = os.getenv("APP_MODE", "cli")
    if app_mode == "cli":
        cli()
    else:
        global app
        app = FastAPI()
        # app.include_router(api_router)


if __name__ == "__main__":
    main()
