import logging

from interactions import (
    Client,
    Intents,
    SlashContext,
    listen,
    slash_command,
)

from src.adapters.ingress.discord import send_error_embed
from src.adapters.ingress.discord.commands import *  # noqa: F401, F403
from src.common.constants import DISCORD_BOT_TOKEN
from src.common.logging import configure_logger, get_logger

logger = get_logger(__name__)

bot = Client(intents=Intents.DEFAULT)


@slash_command(name="hello", description="foobar")
async def hello(ctx: SlashContext) -> None:
    return await send_error_embed(ctx, "Foobar!")


@listen()
async def on_ready() -> None:
    logger.info("Ready")
    logger.info(f"This bot is owned by {bot.owner}")


configure_logger(logging.INFO)
bot.start(DISCORD_BOT_TOKEN)
