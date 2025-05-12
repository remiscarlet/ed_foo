from collections import defaultdict
from itertools import batched
from pprint import pformat

from interactions import Embed, OptionType, SlashContext, slash_command, slash_option

from src.adapters.ingress.discord import send_error_embed
from src.adapters.persistence.postgresql.adapter import (
    ApiCommandAdapter,
    SystemsAdapter,
)
from src.adapters.persistence.postgresql.types import HotspotResult
from src.common.logging import get_logger

logger = get_logger(__name__)


@slash_command(name="get-hotspots", description="Get list of hotspots in a given system")
@slash_option(
    name="system_name_option", description="Target system name to acquire", required=True, opt_type=OptionType.STRING
)
async def get_hotspots(ctx: SlashContext, system_name_option: str) -> None:
    await ctx.defer(ephemeral=True)

    try:
        SystemsAdapter().get_system(system_name_option)
    except ValueError:
        return await send_error_embed(ctx, f"Could not find system '{system_name_option}'!")

    hotspots = ApiCommandAdapter().get_hotspots_in_system(system_name_option)

    results_by_commodity: dict[str, list[HotspotResult]] = defaultdict(lambda: list())
    for hotspot in hotspots:
        name = hotspot.commodity
        results_by_commodity[name].append(hotspot)

    logger.info(pformat(results_by_commodity))

    embeds: list[Embed] = []
    for commodity_name in sorted(results_by_commodity.keys()):
        hotspots = results_by_commodity[commodity_name]

        ring_names = list(map(lambda hs: f"=> {hs.ring_name} (x{hs.count}) ({hs.ring_type})", hotspots))
        hotspots_str = "**Mine In**:\n"
        hotspots_str += "\n".join(ring_names)
        embed = Embed(
            title=f"{commodity_name} Hotspots ({system_name_option})",
            description=hotspots_str,
            color=0x3498DB,
        )

        embeds.append(embed)

    embeds.sort(key=lambda e: e.title or "")
    for embeds_batch in batched(embeds, 10):
        await ctx.send(embeds=list(embeds_batch), ephemeral=True)
