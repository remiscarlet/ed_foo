import logging

from interactions import (
    Client,
    Intents,
    SlashContext,
    listen,
    slash_command,
)

from src.common.constants import DISCORD_BOT_TOKEN
from src.common.logging import configure_logger, get_logger
from src.interfaces.discord import send_error_embed
from src.interfaces.discord.commands import *  # noqa: F401, F403

logger = get_logger(__name__)

bot = Client(intents=Intents.DEFAULT)


@slash_command(name="hello", description="foobar")
async def hello(ctx: SlashContext) -> None:
    await send_error_embed(ctx, "Foobar!")
    return


@listen()
async def on_ready() -> None:
    logger.info("Ready")
    logger.info(f"This bot is owned by {bot.owner}")


configure_logger(logging.INFO)
bot.start(DISCORD_BOT_TOKEN)
