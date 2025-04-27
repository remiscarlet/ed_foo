from enum import StrEnum
from typing import NamedTuple, Optional, Set, Union


class CommodityCategory(StrEnum):
    CHEMICALS = "Chemicals"
    CONSUMER_ITEMS = "Consumer Items"
    LEGAL_DRUGS = "Legal Drugs"
    FOODS = "Foods"
    INDUSTRIAL_MATERIALS = "Industrial Materials"
    MACHINERY = "Machinery"
    MEDICINES = "Medicines"
    METALS = "Metals"
    MINERALS = "Minerals"
    SALVAGE = "Salvage"
    SLAVERY = "Slavery"
    TECHNOLOGY = "Technology"
    TEXTILES = "Textiles"
    WASTE = "Waste"
    WEAPONS = "Weapons"


class Chemicals(StrEnum):
    TRITIUM = "Tritium"
    ARGONOMIC_TREATMENT = "Argonomic Treatment"
    EXPLOSIVES = "Explosives"
    HYDROGEN_FUEL = "Hydrogen Fuel"
    LIQUID_FUEL = "Liquid Fuel"
    MINERAL_OIL = "Mineral Oil"
    NERVE_AGENTS = "Nerve Agents"
    PESTICIDES = "Pesticides"
    ROCKFORTH_FERTILISER = "Rockforth Fertiliser"
    SURFACE_STABILISERS = "Surface Stabilisers"
    SYNTHETIC_REAGENTS = "Synthetic Reagents"
    WATER = "Water"


class Minerals(StrEnum):
    ALEXANDRITE = "Alexandrite"
    BAUXITE = "Bauxite"
    BENITOITE = "Benitoite"
    BERTRANDITE = "Bertrandite"
    BROMELLITE = "Bromellite"
    COLTAN = "Coltan"
    CRYOLITE = "Cryolite"
    GALLITE = "Gallite"
    GOSLARITE = "Goslarite"
    GRANDIDIERITE = "Grandidierite"
    HAEMATITE = "Haematite"
    INDITE = "Indite"
    JADEITE = "Jadeite"
    LEPIDOLITE = "Lepidolite"
    LITHIUM_HYDROXIDE = "Lithium Hydroxide"
    LOW_TEMPERATURE_DIAMONDS = "Low Temperature Diamonds"
    METHANE_CLATHRATE = "Methane Clathrate"
    METHANOL_MONOHYDRATE_CRYSTALS = "Methanol Monohydrate Crystals"
    MOISSANITE = "Moissanite"
    MONAZITE = "Monazite"
    MUSGRAVITE = "Musgravite"
    PAINITE = "Painite"
    PYROPHYLLITE = "Pyrophyllite"
    RHODPLUMSITE = "Rhodplumsite"
    RUTILE = "Rutile"
    SERENDIBITE = "Serendibite"
    TAAFFEITE = "Taaffeite"
    URANINITE = "Uraninite"
    VOID_OPAL = "Void Opal"


class Metals(StrEnum):
    ALUMINIUM = "Aluminium"
    BERYLLIUM = "Beryllium"
    BISMUTH = "Bismuth"
    COBALT = "Cobalt"
    COPPER = "Copper"
    GALLIUM = "Gallium"
    GOLD = "Gold"
    HAFNIUM_178 = "Hafnium 178"
    INDIUM = "Indium"
    LANTHANUM = "Lanthanum"
    LITHIUM = "Lithium"
    OSMIUM = "Osmium"
    PALLADIUM = "Palladium"
    PLATINUM = "Platinum"
    PRASEODYMIUM = "Praseodymium"
    SAMARIUM = "Samarium"
    SILVER = "Silver"
    STEEL = "Steel"
    TANTALUM = "Tantalum"
    THALLIUM = "Thallium"
    THORIUM = "Thorium"
    TITANIUM = "Titanium"
    URANIUM = "Uranium"


Commodity = Union[Minerals, Metals, Chemicals]


class MiningMethod(StrEnum):
    LASER_MINING = "Laser Mining"
    CORE_MINING = "Core Mining"


class RingType(StrEnum):
    ICY = "Icy"
    METALLIC = "Metallic"
    METAL_RICH = "Metal Rich"
    ROCKY = "Rocky"


class MineableMetadata(NamedTuple):
    ring_types: Set[RingType] = set()
    mining_method: Optional[MiningMethod] = None
    has_hotspots: Optional[bool] = None


# Data from https://tinyurl.com/bdd435s5
_MINEABLE_METADATA: dict[Commodity, MineableMetadata] = {
    # Chemicals
    Chemicals.TRITIUM: MineableMetadata(
        ring_types={RingType.METAL_RICH}, mining_method=MiningMethod.LASER_MINING, has_hotspots=True
    ),
    # Minerals
    Minerals.ALEXANDRITE: MineableMetadata(
        ring_types={RingType.ROCKY, RingType.METAL_RICH, RingType.ICY},
        mining_method=MiningMethod.CORE_MINING,
        has_hotspots=True,
    ),
    Minerals.BAUXITE: MineableMetadata(
        ring_types={RingType.ROCKY}, mining_method=MiningMethod.LASER_MINING, has_hotspots=False
    ),
    Minerals.BENITOITE: MineableMetadata(
        ring_types={RingType.ROCKY}, mining_method=MiningMethod.CORE_MINING, has_hotspots=True
    ),
    Minerals.BERTRANDITE: MineableMetadata(
        ring_types={RingType.METALLIC}, mining_method=MiningMethod.LASER_MINING, has_hotspots=False
    ),
    Minerals.BROMELLITE: MineableMetadata(
        ring_types={RingType.ICY}, mining_method=MiningMethod.CORE_MINING, has_hotspots=True
    ),
    Minerals.COLTAN: MineableMetadata(
        ring_types={RingType.ROCKY}, mining_method=MiningMethod.LASER_MINING, has_hotspots=False
    ),
    Minerals.GALLITE: MineableMetadata(
        ring_types={RingType.METALLIC}, mining_method=MiningMethod.LASER_MINING, has_hotspots=False
    ),
    Minerals.GRANDIDIERITE: MineableMetadata(
        ring_types={RingType.ROCKY, RingType.ICY},
        mining_method=MiningMethod.CORE_MINING,
        has_hotspots=True,
    ),
    Minerals.INDITE: MineableMetadata(
        ring_types={RingType.METALLIC}, mining_method=MiningMethod.LASER_MINING, has_hotspots=False
    ),
    Minerals.LEPIDOLITE: MineableMetadata(
        ring_types={RingType.METALLIC}, mining_method=MiningMethod.LASER_MINING, has_hotspots=False
    ),
    Minerals.LITHIUM_HYDROXIDE: MineableMetadata(
        ring_types={RingType.METALLIC}, mining_method=MiningMethod.LASER_MINING, has_hotspots=False
    ),
    Minerals.LOW_TEMPERATURE_DIAMONDS: MineableMetadata(
        mining_method=MiningMethod.CORE_MINING,
        ring_types={RingType.ICY},
        has_hotspots=True,
    ),
    Minerals.METHANE_CLATHRATE: MineableMetadata(
        ring_types={RingType.METALLIC}, mining_method=MiningMethod.LASER_MINING, has_hotspots=False
    ),
    Minerals.METHANOL_MONOHYDRATE_CRYSTALS: MineableMetadata(
        ring_types={RingType.METALLIC}, mining_method=MiningMethod.LASER_MINING, has_hotspots=False
    ),
    Minerals.MONAZITE: MineableMetadata(
        ring_types={RingType.ROCKY, RingType.METAL_RICH, RingType.METALLIC},
        mining_method=MiningMethod.CORE_MINING,
        has_hotspots=True,
    ),
    Minerals.MUSGRAVITE: MineableMetadata(
        mining_methods=MiningMethod.CORE_MINING,
        ring_types={RingType.ROCKY},
        has_hotspots=True,
    ),
    Minerals.PAINITE: MineableMetadata(
        ring_types={RingType.METALLIC}, mining_method=MiningMethod.LASER_MINING, has_hotspots=True
    ),
    Minerals.RHODPLUMSITE: MineableMetadata(
        ring_types={RingType.ROCKY, RingType.METAL_RICH, RingType.METALLIC},
        mining_method=MiningMethod.CORE_MINING,
        has_hotspots=True,
    ),
    Minerals.RUTILE: MineableMetadata(
        ring_types={RingType.METALLIC}, mining_method=MiningMethod.LASER_MINING, has_hotspots=False
    ),
    Minerals.SERENDIBITE: MineableMetadata(
        ring_types={RingType.ROCKY, RingType.METAL_RICH, RingType.METALLIC},
        mining_method=MiningMethod.CORE_MINING,
        has_hotspots=True,
    ),
    Minerals.URANINITE: MineableMetadata(
        ring_types={RingType.METALLIC}, mining_method=MiningMethod.LASER_MINING, has_hotspots=False
    ),
    Minerals.VOID_OPAL: MineableMetadata(
        mining_methods=MiningMethod.CORE_MINING,
        ring_types={RingType.ICY},
        has_hotspots=True,
    ),
    # Metals
    Metals.COBALT: MineableMetadata(
        ring_types={RingType.ROCKY}, mining_method=MiningMethod.LASER_MINING, has_hotspots=False
    ),
    Metals.GOLD: MineableMetadata(
        ring_types={RingType.METALLIC}, mining_method=MiningMethod.LASER_MINING, has_hotspots=False
    ),
    Metals.OSMIUM: MineableMetadata(
        ring_types={RingType.METALLIC}, mining_method=MiningMethod.LASER_MINING, has_hotspots=False
    ),
    Metals.PALLADIUM: MineableMetadata(
        ring_types={RingType.METALLIC}, mining_method=MiningMethod.LASER_MINING, has_hotspots=False
    ),
    Metals.PLATINUM: MineableMetadata(
        mining_method=MiningMethod.LASER_MINING,
        ring_types={RingType.METALLIC},
        has_hotspots=True,
    ),
    Metals.PRASEODYMIUM: MineableMetadata(
        ring_types={RingType.METALLIC}, mining_method=MiningMethod.LASER_MINING, has_hotspots=False
    ),
    Metals.SAMARIUM: MineableMetadata(
        ring_types={RingType.METALLIC}, mining_method=MiningMethod.LASER_MINING, has_hotspots=False
    ),
    Metals.SILVER: MineableMetadata(
        ring_types={RingType.METALLIC}, mining_method=MiningMethod.LASER_MINING, has_hotspots=False
    ),
}
