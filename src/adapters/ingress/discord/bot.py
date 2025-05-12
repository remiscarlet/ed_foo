import logging

from interactions import (
    Client,
    Intents,
    listen,
)

from src.adapters.ingress.discord.commands import *  # noqa: F401, F403
from src.common.constants import DISCORD_BOT_TOKEN
from src.common.logging import configure_logger, get_logger

logger = get_logger(__name__)

bot = Client(intents=Intents.DEFAULT)


@listen()
async def on_ready() -> None:
    logger.info("Ready")
    logger.info(f"This bot is owned by {bot.owner}")


configure_logger(logging.INFO)
bot.start(DISCORD_BOT_TOKEN)
