from datetime import datetime, timedelta, timezone
from pprint import pformat
from typing import Dict, List, Optional

from src.db import SystemDB
from src.logging import get_logger
from src.types import PowerplaySystem

logger = get_logger(__name__)


class PowerplaySystems:
    systems: Dict[str, PowerplaySystem] = {}
    db = SystemDB()

    @staticmethod
    def get_acquisition_systems(
        power: str, factionStates: Optional[List[str]] = None, maxAgeInDays: int = 2
    ) -> List[PowerplaySystem]:
        """
        Args:
            power (str): _description_
            factionStates (Optional[List[str]], optional): _description_. Defaults to None.
            maxAgeInDays (int, optional): We rely on the faction state being accurate to
                                          determine what stations to check. Defaults to 2.

        Returns:
            _type_: _description_
        """

        def predicates(system: PowerplaySystem) -> bool:
            validAge = (datetime.now(timezone.utc) - system.date) < timedelta(days=maxAgeInDays)
            validStates = True if factionStates is None else system.controlling_faction_in_states(factionStates)
            return validAge and validStates

        systems = [
            system for system in PowerplaySystems.db.get_unoccupied_powerplay_systems(power) if predicates(system)
        ]

        logger.debug(
            pformat(
                {
                    "power": power,
                    "factionStates": factionStates,
                    "num_all_systems": len(systems),
                }
            )
        )
        return systems

    @staticmethod
    def get_reinforcement_systems(
        power: str,
        powerStates: Optional[List[str]] = None,
        factionStates: Optional[List[str]] = None,
        maxAgeInDays: int = 2,
    ) -> List[PowerplaySystem]:
        def predicates(system: PowerplaySystem) -> bool:
            validAge = (datetime.now(timezone.utc) - system.date) < timedelta(days=maxAgeInDays)
            validState = system.controlling_faction_in_states(factionStates) if factionStates else True
            return validAge and validState

        systems = [
            system for system in PowerplaySystems.db.get_powerplay_systems(power, powerStates) if predicates(system)
        ]

        logger.debug(
            pformat(
                {
                    "power": power,
                    "powerStates": powerStates,
                    "factionStates": factionStates,
                    "num_all_systems": len(systems),
                }
            )
        )

        return systems
