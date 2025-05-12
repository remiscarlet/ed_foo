import logging
from collections import namedtuple
from pprint import pformat

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

from src.adapters.persistence.postgresql.adapter import (
    ApiCommandAdapter,
    SystemsAdapter,
)
from src.adapters.persistence.postgresql.types import MiningAcquisitionResult
from src.common.constants import DISCORD_BOT_TOKEN
from src.common.logging import configure_logger, get_logger

logger = get_logger(__name__)

bot = Client(intents=Intents.DEFAULT)


@listen()
async def on_ready() -> None:
    logger.info("Ready")
    logger.info(f"This bot is owned by {bot.owner}")


async def send_error_embed(ctx: SlashContext, msg: str) -> None:
    await ctx.send(
        embed=Embed(
            title="Error!",
            description=msg,
            color=0xFF1111,
        ),
        ephemeral=True,
    )


StationAndPrice = namedtuple("StationAndPrice", ["station", "price", "demand"])


class MineableDataDisplay:
    name: str
    mineable_rings: set[str]
    sell_stations: set[StationAndPrice]

    def __init__(self, commodity_name: str) -> None:
        self.name = commodity_name
        self.mineable_rings = set()
        self.sell_stations = set()

    def add_route(self, route: MiningAcquisitionResult) -> None:
        if route.commodity != self.name:
            raise ValueError(f"Tried adding invalid route for MineableDataDisplay '{self.name}'")

        self.mineable_rings.add(route.ring_name)
        self.sell_stations.add(StationAndPrice(route.station_name, route.sell_price, route.demand))


@slash_command(name="get-mining-expandable", description="Get list of mining routes for acquiring a target system")
@slash_option(
    name="system_name_option", description="Target system name to acquire", required=True, opt_type=OptionType.STRING
)
async def get_mining_expandable(ctx: SlashContext, system_name_option: str) -> None:
    await ctx.defer(ephemeral=True)

    try:
        system = SystemsAdapter().get_system(system_name_option)
    except ValueError:
        return await send_error_embed(ctx, f"Could not find system '{system_name_option}'!")

    if system.power_state != "Unoccupied":
        return await send_error_embed(ctx, f"System '{system_name_option}' is not unoccupied!")

    if "Nakato Kaine" not in (system.powers or []):
        return await send_error_embed(
            ctx, f"Unoccupied system '{system_name_option}' is not within Councillor Kaine's sphere of influence!"
        )

    routes = ApiCommandAdapter().get_mining_expandable_systems_in_range(system_name_option)

    mineable_data: dict[str, MineableDataDisplay] = {}
    for route in routes:
        name = route.commodity
        if name not in mineable_data:
            mineable_data[name] = MineableDataDisplay(name)
        mineable_data[name].add_route(route)

    logger.info(pformat(mineable_data))

    embeds: list[Embed] = []
    for name, data in mineable_data.items():
        mine_in = "**Mine In:**\n"
        for ring in data.mineable_rings:
            mine_in += f"-> {ring}\n"

        embed = Embed(
            title=f"{name} Mining Routes - Acquiring {system_name_option}",
            description=mine_in,
            color=0x3498DB,
        )

        embed.add_field("---------", "**Sell At:**")

        for station_price in data.sell_stations:
            embed.add_field(
                f"{station_price.station} ({system_name_option})",
                f"{station_price.price:3,} CR w/ {station_price.demand:3,} Dem",
            )

        embeds.append(embed)

    embeds.sort(key=lambda e: e.title or "")
    await ctx.send(embeds=embeds, ephemeral=True)


configure_logger(logging.INFO)
bot.start(DISCORD_BOT_TOKEN)
