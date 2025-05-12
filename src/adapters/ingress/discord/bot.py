from interactions import (
    Client,
    Embed,
    Intents,
    OptionType,
    SlashContext,
    listen,
    slash_command,
    slash_option,
)
from tabulate import tabulate

from src.adapters.persistence.postgresql.adapter import ApiCommandAdapter
from src.common.constants import DISCORD_BOT_TOKEN
from src.common.logging import get_logger

logger = get_logger(__name__)

bot = Client(intents=Intents.DEFAULT)


@listen()
async def on_ready() -> None:
    print("Ready")
    print(f"This bot is owned by {bot.owner}")


@slash_command(name="get-mining-expandable", description="Get list of mining routes for acquiring a target system")
@slash_option(
    name="system_name_option", description="Target system name to acquire", required=True, opt_type=OptionType.STRING
)
async def get_mining_expandable(ctx: SlashContext, system_name_option: str) -> None:
    await ctx.defer(ephemeral=True)
    routes = ApiCommandAdapter().get_mining_expandable_systems_in_range(system_name_option)

    msg = (
        "```====== DETAILS ======\n"
        f"Target Unoccupied System: {system_name_option}\n\n"
        "====== MINING ACQUISITION ROUTES ======\n"
    )

    headers = ["Mine", "In", "Sell In", "At", "For", "Demand"]
    table = [
        [r.commodity, r.ring_name, r.unoccupied_system, r.station_name, f"{r.sell_price:3,} CR", f"{r.demand:3,}"]
        for r in routes
    ]
    msg += tabulate(table, headers)
    msg += "\n```"

    embed = Embed(title=f"Mining Acquisition For {system_name_option}", description=msg, color=0x3498DB)  # A nice blue

    await ctx.send(embeds=embed, ephemeral=True)


bot.start(DISCORD_BOT_TOKEN)
