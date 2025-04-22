from argparse import Action, ArgumentParser, Namespace
from typing import Any, List, Optional, Sequence, cast

from src.logging import get_logger
from src.populated_galaxy_systems import PopulatedGalaxySystems
from src.types import Coordinates, HasMineableMetadata, Mineables

logger = get_logger(__name__)


class StoreSystemNameWithCoords(Action):
    def __call__(
        self, parser: ArgumentParser, namespace: Namespace, values: Any, option_string: Optional[str] = None
    ) -> None:
        setattr(namespace, self.dest, values)
        system = PopulatedGalaxySystems.get_system(values)
        coords = Coordinates(0, 0, 0) if system is None else system.coords
        setattr(namespace, "current_coords", coords)


class StoreMineableCommodities(Action):
    default_commodities = [
        Mineables.MONAZITE,  # type: ignore
        Mineables.PLATINUM,  # type: ignore
    ]

    def __mineables_to_enriched_enum(self, mineables: List[Mineables]) -> List[HasMineableMetadata]:
        enriched_mineables = []
        for mineable in mineables:
            enriched_mineables.append(mineable.getMineableMetadata())
        return enriched_mineables

    def __init__(self, option_strings: Sequence[str], dest: str, **kwargs: Any) -> None:
        raw_default = kwargs.pop("default", self.default_commodities)
        processed = self.__mineables_to_enriched_enum(cast(List[Mineables], list(raw_default)))

        kwargs["default"] = processed
        super().__init__(option_strings, dest, **kwargs)

    _is_first_invocation = True

    def __call__(
        self, parser: ArgumentParser, namespace: Namespace, values: Any, option_string: Optional[str] = None
    ) -> None:
        # Ugly
        if self._is_first_invocation:
            setattr(namespace, self.dest, [])
            self._is_first_invocation = False

        lst = getattr(namespace, self.dest)
        lst.extend(self.__mineables_to_enriched_enum([Mineables(values)]))

        setattr(namespace, self.dest, lst)
