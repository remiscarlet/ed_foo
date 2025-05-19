import asyncio
import os

from fastapi import FastAPI

from src.interfaces.cli.router import cli

app = None


async def run() -> None:
    app_mode = os.getenv("APP_MODE", "cli")
    if app_mode == "cli":
        cli()
    else:
        global app
        app = FastAPI()
        # app.include_router(api_router)


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
