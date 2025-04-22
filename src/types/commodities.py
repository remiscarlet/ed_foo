from itertools import chain
from typing import (
    Iterable,
    NotRequired,
    Protocol,
    Set,
    TypedDict,
    cast,
)

from aenum import StrEnum, extend_enum


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
    SLAVES = "Slaves"
    TECHNOLOGY = "Technology"
    TEXTILES = "Textiles"
    WASTE = "Waste"
    WEAPONS = "Weapons"


class MiningMethod(StrEnum):
    LASER_MINING = "Laser Mining"
    CORE_MINING = "Core Mining"


class RingType(StrEnum):
    ICY = "Icy"
    METALLIC = "Metallic"
    METAL_RICH = "Metal Rich"
    ROCKY = "Rocky"


type CommodityEnumTuple = tuple[str, bool, str, set[MiningMethod], set[RingType], bool]


class MineableMetadata(TypedDict):
    mining_methods: Set[MiningMethod]
    ring_types: Set[RingType]
    has_hotspots: bool

    symbol: NotRequired[str]  # This is okay to be a str as we convert it to a MineableSymbols


def mineableCommodityEnum(value: str, metadata: MineableMetadata) -> CommodityEnumTuple:
    is_mineable = True
    return (
        value,
        is_mineable,
        metadata.get("symbol", value),
        metadata["mining_methods"],
        metadata["ring_types"],
        metadata["has_hotspots"],
    )


def commodityEnum(value: str) -> CommodityEnumTuple:
    [is_mineable, mineable_symbol, mining_methods, ring_types, has_hotspots] = [
        False,
        value,
        set[MiningMethod](),
        set[RingType](),
        False,
    ]
    return (value, is_mineable, mineable_symbol, mining_methods, ring_types, has_hotspots)


aenum_metadata_init_config = "value is_mineable symbol mining_methods ring_types has_hotspots"


class Chemicals(StrEnum):
    """
    Thanks, Tritium.
    """

    _init_ = aenum_metadata_init_config
    mining_methods: Set[MiningMethod]
    ring_types: Set[RingType]
    has_hotspots: bool
    is_mineable: bool
    TRITIUM = mineableCommodityEnum(
        value="Tritium",
        metadata={
            "mining_methods": {MiningMethod.LASER_MINING},
            "ring_types": {RingType.ICY},
            "has_hotspots": True,
        },
    )

    ARGONOMIC_TREATMENT = commodityEnum(value="Argonomic Treatment")
    EXPLOSIVES = commodityEnum(value="Explosives")
    HYDROGEN_FUEL = commodityEnum(value="Hydrogen Fuel")
    LIQUID_FUEL = commodityEnum(value="Liquid Fuel")
    MINERAL_OIL = commodityEnum(value="Mineral Oil")
    NERVE_AGENTS = commodityEnum(value="Nerve Agents")
    PESTICIDES = commodityEnum(value="Pesticides")
    ROCKFORTH_FERTILISER = commodityEnum(value="Rockforth Fertiliser")
    SURFACE_STABILISERS = commodityEnum(value="Surface Stabilisers")
    SYNTHETIC_REAGENTS = commodityEnum(value="Synthetic Reagents")

    WATER = commodityEnum(value="Water")


# Data from https://tinyurl.com/bdd435s5
class Minerals(StrEnum):
    _init_ = aenum_metadata_init_config
    mining_methods: Set[MiningMethod]
    ring_types: Set[RingType]
    has_hotspots: bool
    is_mineable: bool

    ALEXANDRITE = mineableCommodityEnum(
        value="Alexandrite",
        metadata={
            "mining_methods": {MiningMethod.CORE_MINING},
            "ring_types": {RingType.ROCKY, RingType.METAL_RICH, RingType.ICY},
            "has_hotspots": True,
        },
    )
    BAUXITE = mineableCommodityEnum(
        value="Bauxite",
        metadata={
            "mining_methods": {MiningMethod.LASER_MINING},
            "ring_types": {RingType.ROCKY},
            "has_hotspots": False,
        },
    )
    BENITOITE = mineableCommodityEnum(
        value="Benitoite",
        metadata={
            "mining_methods": {MiningMethod.CORE_MINING},
            "ring_types": {RingType.ROCKY},
            "has_hotspots": True,
        },
    )
    BERTRANDITE = mineableCommodityEnum(
        value="Bertrandite",
        metadata={
            "mining_methods": {MiningMethod.LASER_MINING},
            "ring_types": {RingType.METALLIC},
            "has_hotspots": False,
        },
    )
    BROMELLITE = mineableCommodityEnum(
        value="Bromellite",
        metadata={
            "mining_methods": {MiningMethod.CORE_MINING, MiningMethod.LASER_MINING},
            "ring_types": {RingType.ICY},
            "has_hotspots": True,
        },
    )
    COLTAN = mineableCommodityEnum(
        value="Coltan",
        metadata={
            "mining_methods": {MiningMethod.LASER_MINING},
            "ring_types": {RingType.ROCKY},
            "has_hotspots": False,
        },
    )
    CRYOLITE = commodityEnum(value="Cryolite")
    GALLITE = mineableCommodityEnum(
        value="Gallite",
        metadata={
            "mining_methods": {MiningMethod.LASER_MINING},
            "ring_types": {RingType.METALLIC},
            "has_hotspots": False,
        },
    )
    GOSLARITE = commodityEnum(value="Goslarite")
    GRANDIDIERITE = mineableCommodityEnum(
        value="Grandidierite",
        metadata={
            "mining_methods": {MiningMethod.CORE_MINING},
            "ring_types": {RingType.ROCKY, RingType.ICY},
            "has_hotspots": True,
        },
    )
    HAEMATITE = commodityEnum(value="Haematite")
    INDITE = mineableCommodityEnum(
        value="Indite",
        metadata={
            "mining_methods": {MiningMethod.LASER_MINING},
            "ring_types": {RingType.METALLIC},
            "has_hotspots": False,
        },
    )
    JADEITE = commodityEnum(value="Jadeite")
    LEPIDOLITE = mineableCommodityEnum(
        value="Lepidolite",
        metadata={
            "mining_methods": {MiningMethod.LASER_MINING},
            "ring_types": {RingType.METALLIC},
            "has_hotspots": False,
        },
    )
    LITHIUM_HYDROXIDE = mineableCommodityEnum(
        value="Lithium Hydroxide",
        metadata={
            "mining_methods": {MiningMethod.LASER_MINING},
            "ring_types": {RingType.METALLIC},
            "has_hotspots": False,
        },
    )
    LOW_TEMPERATURE_DIAMONDS = mineableCommodityEnum(
        value="Low Temperature Diamonds",
        metadata={
            "mining_methods": {MiningMethod.CORE_MINING},
            "symbol": "LowTemperatureDiamond",
            "ring_types": {RingType.ICY},
            "has_hotspots": True,
        },
    )
    METHANE_CLATHRATE = mineableCommodityEnum(
        value="Methane Clathrate",
        metadata={
            "mining_methods": {MiningMethod.LASER_MINING},
            "ring_types": {RingType.METALLIC},
            "has_hotspots": False,
        },
    )
    METHANOL_MONOHYDRATE_CRYSTALS = mineableCommodityEnum(
        value="Methanol Monohydrate Crystals",
        metadata={
            "mining_methods": {MiningMethod.LASER_MINING},
            "ring_types": {RingType.METALLIC},
            "has_hotspots": False,
        },
    )
    MOISSANITE = commodityEnum(value="Moissanite")
    MONAZITE = mineableCommodityEnum(
        value="Monazite",
        metadata={
            "mining_methods": {MiningMethod.CORE_MINING},
            "ring_types": {RingType.ROCKY, RingType.METAL_RICH, RingType.METALLIC},
            "has_hotspots": True,
        },
    )
    MUSGRAVITE = mineableCommodityEnum(
        value="Musgravite",
        metadata={"mining_methods": {MiningMethod.CORE_MINING}, "ring_types": {RingType.ROCKY}, "has_hotspots": True},
    )
    PAINITE = mineableCommodityEnum(
        value="Painite",
        metadata={
            "mining_methods": {MiningMethod.LASER_MINING},
            "ring_types": {RingType.METALLIC},
            "has_hotspots": True,
        },
    )
    PYROPHYLLITE = commodityEnum(value="Pyrophyllite")
    RHODPLUMSITE = mineableCommodityEnum(
        value="Rhodplumsite",
        metadata={
            "mining_methods": {MiningMethod.CORE_MINING},
            "ring_types": {RingType.ROCKY, RingType.METAL_RICH, RingType.METALLIC},
            "has_hotspots": True,
        },
    )
    RUTILE = mineableCommodityEnum(
        value="Rutile",
        metadata={
            "mining_methods": {MiningMethod.LASER_MINING},
            "ring_types": {RingType.METALLIC},
            "has_hotspots": False,
        },
    )
    SERENDIBITE = mineableCommodityEnum(
        value="Serendibite",
        metadata={
            "mining_methods": {MiningMethod.CORE_MINING},
            "ring_types": {RingType.ROCKY, RingType.METAL_RICH, RingType.METALLIC},
            "has_hotspots": True,
        },
    )
    TAAFFEITE = commodityEnum(value="Taaffeite")
    URANINITE = mineableCommodityEnum(
        value="Uraninite",
        metadata={
            "mining_methods": {MiningMethod.LASER_MINING},
            "ring_types": {RingType.METALLIC},
            "has_hotspots": False,
        },
    )
    VOID_OPAL = mineableCommodityEnum(
        value="Void Opal",
        metadata={
            "mining_methods": {MiningMethod.CORE_MINING},
            "symbol": "Opal",
            "ring_types": {RingType.ICY},
            "has_hotspots": True,
        },
    )


class Metals(StrEnum):
    _init_ = aenum_metadata_init_config
    mining_methods: Set[MiningMethod]
    ring_types: Set[RingType]
    has_hotspots: bool
    is_mineable: bool

    ALUMINIUM = commodityEnum(value="Aluminium")
    BERYLLIUM = commodityEnum(value="Beryllium")
    BISMUTH = commodityEnum(value="Bismuth")
    COBALT = mineableCommodityEnum(
        value="Cobalt",
        metadata={
            "mining_methods": {MiningMethod.LASER_MINING},
            "ring_types": {RingType.ROCKY},
            "has_hotspots": False,
        },
    )
    COPPER = commodityEnum(value="Copper")
    GALLIUM = commodityEnum(value="Gallium")
    GOLD = mineableCommodityEnum(
        value="Gold",
        metadata={
            "mining_methods": {MiningMethod.LASER_MINING},
            "ring_types": {RingType.METALLIC},
            "has_hotspots": False,
        },
    )
    HAFNIUM_178 = commodityEnum(value="Hafnium 178")
    INDIUM = commodityEnum(value="Indium")
    LANTHANUM = commodityEnum(value="Lanthanum")
    LITHIUM = commodityEnum(value="Lithium")
    OSMIUM = mineableCommodityEnum(
        value="Osmium",
        metadata={
            "mining_methods": {MiningMethod.LASER_MINING},
            "ring_types": {RingType.METALLIC},
            "has_hotspots": False,
        },
    )
    PALLADIUM = mineableCommodityEnum(
        value="Palladium",
        metadata={
            "mining_methods": {MiningMethod.LASER_MINING},
            "ring_types": {RingType.METALLIC},
            "has_hotspots": False,
        },
    )
    PLATINUM = mineableCommodityEnum(
        value="Platinum",
        # Technically can also be core mined but who does...
        # But also complicates metadata because it can be core mined in more ring types
        metadata={
            "mining_methods": {MiningMethod.LASER_MINING},
            "ring_types": {RingType.METALLIC},
            "has_hotspots": True,
        },
    )
    PRASEODYMIUM = mineableCommodityEnum(
        value="Praseodymium",
        metadata={
            "mining_methods": {MiningMethod.LASER_MINING},
            "ring_types": {RingType.METALLIC},
            "has_hotspots": False,
        },
    )
    SAMARIUM = mineableCommodityEnum(
        value="Samarium",
        metadata={
            "mining_methods": {MiningMethod.LASER_MINING},
            "ring_types": {RingType.METALLIC},
            "has_hotspots": False,
        },
    )
    SILVER = mineableCommodityEnum(
        value="Silver",
        metadata={
            "mining_methods": {MiningMethod.LASER_MINING},
            "ring_types": {RingType.METALLIC},
            "has_hotspots": False,
        },
    )
    STEEL = commodityEnum(value="Steel")
    TANTALUM = commodityEnum(value="Tantalum")
    THALLIUM = commodityEnum(value="Thallium")
    THORIUM = commodityEnum(value="Thorium")
    TITANIUM = commodityEnum(value="Titanium")
    URANIUM = commodityEnum(value="Uranium")


mineables_lookup = {m.value: m for m in chain(Minerals, Metals, Chemicals)}


class HasMineableMetadata(Protocol):
    # Enum field
    name: str
    value: str

    # Metadata fields
    symbol: str  # Should be MineableSymbols but hard to do because we dynamically add its members, leading to circ deps
    is_mineable: bool
    mining_methods: Set[MiningMethod]
    ring_types: Set[RingType]
    has_hotspots: bool


class Mineables(StrEnum):
    def getMineableMetadata(self) -> HasMineableMetadata:
        return cast(HasMineableMetadata, mineables_lookup[self.value])


mineable_symbols_lookup = {m.symbol: m for m in cast(Iterable[HasMineableMetadata], chain(Minerals, Metals, Chemicals))}


class MineableSymbols(StrEnum):
    def getMineableMetadata(self) -> HasMineableMetadata:
        return mineable_symbols_lookup[self.value]


mineable_categories = cast(Iterable[HasMineableMetadata], chain(Minerals, Metals, Chemicals))
for item in mineable_categories:
    if item.is_mineable:
        extend_enum(Mineables, item.name, item.value)
        extend_enum(MineableSymbols, item.name, item.symbol)


commodity_lookup = {m.value: m for m in chain(Minerals, Metals, Chemicals)}


class CommodityType(StrEnum):
    def getMineableMetadata(self) -> HasMineableMetadata:
        return cast(HasMineableMetadata, commodity_lookup[self.value])


all_commodities = {e.name: e.value for e in chain(Minerals, Metals, Chemicals)}
for name, value in all_commodities.items():
    extend_enum(CommodityType, name, value)
