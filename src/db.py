import dataclasses
import json
import sqlite3
import traceback
from pprint import pformat
from typing import Any, Dict, List, Optional

from src.constants import DB_DATA_PATH
from src.logging import get_logger
from src.types import PowerplaySystem, System

logger = get_logger(__name__)


class SystemDB:
    __table_name = "system"
    __conn: sqlite3.Connection

    def __init__(self) -> None:
        self.__conn = sqlite3.connect(DB_DATA_PATH)
        self.__conn.row_factory = sqlite3.Row
        self.__conn.isolation_level = None

        # https://phiresky.github.io/blog/2020/sqlite-performance-tuning/
        self.__conn.execute("PRAGMA journal_mode = WAL;")
        self.__conn.execute("PRAGMA synchronous = normal;")
        self.__conn.execute("PRAGMA temp_store = memory;")
        self.__conn.execute("PRAGMA mmap_size = 30000000000;")
        self.__conn.execute("PRAGMA page_size = 32768;")
        self.__conn.execute("PRAGMA busy_timeout = 5000;")

        self.init_tables()

    def init_tables(self) -> None:
        init_schema_query = """
            CREATE TABLE IF NOT EXISTS {table_name} (
                id64 INTEGER PRIMARY KEY,
                allegiance TEXT,
                bodies TEXT,
                controllingFaction TEXT,
                coords TEXT,
                date TEXT,
                factions TEXT,
                government TEXT,
                name TEXT,
                population INTEGER,
                primaryEconomy TEXT,
                secondaryEconomy TEXT,
                security TEXT,
                stations TEXT,

                bodyCount TEXT,

                controllingPower TEXT,
                powerConflictProgress TEXT,
                powerState TEXT,
                powerStateControlProgress REAL,
                powerStateReinforcement REAL,
                powerStateUndermining REAL,
                powers TEXT,

                thargoidWar REAL,
                timestamps TEXT
            );
            CREATE UNIQUE INDEX IF NOT EXISTS system_name_idx
                ON {table_name}(name);
            CREATE INDEX IF NOT EXISTS controlling_power_idx
                ON {table_name}(controllingPower);
            CREATE INDEX IF NOT EXISTS power_state_controlling_power_idx
                ON {table_name}(powerState, controllingPower);
            CREATE INDEX IF NOT EXISTS power_state_idx
                ON {table_name}(powerState);
        """
        query = init_schema_query.format(table_name=self.__table_name)

        logger.debug(query)
        self.__conn.executescript(query)
        self.__conn.commit()

    def upsert_system(self, system: System) -> None:
        query_fmt = """
        INSERT INTO
            {table_name} ({column_list})
        VALUES
        (
            {quoted_and_comma_separated_values_list}
        )
        ON CONFLICT (id64) DO
        UPDATE SET
            allegiance = excluded.allegiance,
            bodies = excluded.bodies,
            controllingFaction = excluded.controllingFaction,
            coords = excluded.coords,
            date = excluded.date,
            factions = excluded.factions,
            government = excluded.government,
            name = excluded.name,
            population = excluded.population,
            primaryEconomy = excluded.primaryEconomy,
            secondaryEconomy = excluded.secondaryEconomy,
            security = excluded.security,
            stations = excluded.stations,

            bodyCount = excluded.bodyCount,
            controllingPower = excluded.controllingPower,
            powerConflictProgress = excluded.powerConflictProgress,
            powerState = excluded.powerState,
            powerStateControlProgress = excluded.powerStateControlProgress,
            powerStateReinforcement = excluded.powerStateReinforcement,
            powerStateUndermining = excluded.powerStateUndermining,
            powers = excluded.powers,

            thargoidWar = excluded.thargoidWar,
            timestamps = excluded.timestamps
        """

        with self.__conn:
            query = query_fmt.format(
                table_name=System.db_table_name(),
                column_list=System.db_column_list(),
                quoted_and_comma_separated_values_list=System.db_values_list(system),
            )
            self.__conn.execute(query)

    system_cols = [field.name for field in dataclasses.fields(System)]

    def _convert_row_dict_to_dataclass_params(
        self, expected_cols: List[str], sys_dict: Dict[str, Any]
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        for col in expected_cols:
            col_val = sys_dict[col]
            if col_val is None:
                params[col] = None
            elif isinstance(col_val, int) or isinstance(col_val, float):
                params[col] = col_val
            else:
                params[col] = json.loads(col_val)
        return params

    system_cols = [field.name for field in dataclasses.fields(System)]

    def get_system(self, system_name: str) -> Optional[System]:
        with self.__conn:
            name = system_name.replace("'", "''")
            query = f"SELECT * FROM {self.__table_name} WHERE name='\"{name}\"'"
            logger.debug(query)
            cur = self.__conn.execute(query)
            fetch = cur.fetchone()

            try:
                return System.from_dict(self._convert_row_dict_to_dataclass_params(self.system_cols, fetch))
            except Exception:
                logger.debug(pformat(fetch.keys()))
                traceback.print_exc()
            return None

    def get_systems(self, system_names: List[str]) -> List[System]:
        with self.__conn:
            names = list(map(lambda n: n.replace("'", "''"), system_names))
            names_str = ", ".join(list(map(lambda n: f"'{n}'", names)))

            query = f"SELECT * FROM {self.__table_name} WHERE name IN ({names_str})"
            logger.debug(query)
            cur = self.__conn.execute(query)
            fetches = cur.fetchall()

            rows = []
            for fetch in fetches:
                rows.append(self._convert_row_dict_to_dataclass_params(self.system_cols, fetch))

            return System.schema().load(rows, many=True)

    powerplay_system_cols = [field.name for field in dataclasses.fields(PowerplaySystem)]

    def get_powerplay_systems(self, power: str, powerStates: Optional[List[str]] = None) -> List[PowerplaySystem]:
        query = (
            "SELECT controllingPower AS power, powerState, id64, name, "
            "coords, date, government, allegiance, factions, powers "
            f"FROM {self.__table_name} "
            f"WHERE controllingPower='\"{power}\"'"
        )

        if powerStates:
            powerStatesStr = ", ".join(list(map(lambda state: f"'\"{state}\"'", powerStates)))
            query += f" AND powerState IN ({powerStatesStr})"

        logger.debug(query)
        return self.__execute_powerplay_system_query(query)

    def get_unoccupied_powerplay_systems(self, power: str) -> List[PowerplaySystem]:
        query = (
            "SELECT controllingPower AS power, powerState, id64, "
            "name, coords, date, government, allegiance, factions, powers "
            f"FROM {self.__table_name} "
            f"WHERE powerState='\"Unoccupied\"' AND EXISTS (SELECT 1 FROM json_each(powers) WHERE value = '{power}')"
        )
        logger.debug(query)
        return self.__execute_powerplay_system_query(query)

    def __execute_powerplay_system_query(self, query: str) -> List[PowerplaySystem]:
        with self.__conn:
            cur = self.__conn.execute(query)
            fetches = cur.fetchall()

            rows = []
            for fetch in fetches:
                rows.append(self._convert_row_dict_to_dataclass_params(self.powerplay_system_cols, fetch))

            return PowerplaySystem.schema().load(rows, many=True)
