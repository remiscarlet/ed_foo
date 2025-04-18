import dataclasses
import json
import pprint
import sqlite3
from typing import Dict, List, Optional

from .constants import DB_DATA_PATH
from .ed_types import PowerplaySystem, System


class SystemDB:
    table_name = "system"
    conn: sqlite3.Connection

    def __init__(self):
        self.conn = sqlite3.connect(DB_DATA_PATH)
        self.conn.row_factory = sqlite3.Row
        self.conn.isolation_level = None

        # https://phiresky.github.io/blog/2020/sqlite-performance-tuning/
        self.conn.execute("PRAGMA journal_mode = WAL;")
        self.conn.execute("PRAGMA synchronous = normal;")
        self.conn.execute("PRAGMA temp_store = memory;")
        self.conn.execute("PRAGMA mmap_size = 30000000000;")
        self.conn.execute("PRAGMA page_size = 32768;")
        self.conn.execute("PRAGMA busy_timeout = 5000;")

        self.init_tables()

    def init_tables(self):
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

        self.conn.executescript(init_schema_query.format(table_name=self.table_name))
        self.conn.commit()

    def upsert_system(self, system: System):
        query = """
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

        with self.conn:
            self.conn.execute(
                query.format(
                    table_name=System.db_table_name(),
                    column_list=System.db_column_list(),
                    quoted_and_comma_separated_values_list=System.db_values_list(
                        system
                    ),
                )
            )

    system_cols = [field.name for field in dataclasses.fields(System)]

    def _convert_row_dict_to_dataclass_params(
        self, expected_cols: List[str], sys_dict: Dict
    ):
        params = {}
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
        with self.conn:
            name = system_name.replace("'", "''")
            cur = self.conn.execute(
                f"SELECT * FROM {self.table_name} WHERE name='\"{name}\"'"
            )
            fetch = cur.fetchone()

            if fetch is None:
                return None
            return System.from_dict(
                self._convert_row_dict_to_dataclass_params(self.system_cols, fetch)
            )

    def get_systems(self, system_names: List[str]) -> Optional[System]:
        with self.conn:
            names = list(map(lambda n: n.replace("'", "''"), system_names))
            names_str = ", ".join(list(map(lambda n: f"'{n}'", names)))
            cur = self.conn.execute(
                f"SELECT * FROM {self.table_name} WHERE name IN ({names_str})"
            )
            fetches = cur.fetchall()

            rows = []
            for fetch in fetches:
                rows.append(
                    self._convert_row_dict_to_dataclass_params(self.system_cols, fetch)
                )

            return System.schema().load(rows, many=True)

    powerplay_system_cols = [
        field.name for field in dataclasses.fields(PowerplaySystem)
    ]

    def get_powerplay_systems(
        self, power: str, powerStates: Optional[List[str]] = None
    ):
        query = (
            "SELECT controllingPower AS power, powerState, id64, name, coords, date, government, allegiance, factions, powers "
            f"FROM {self.table_name} "
            f"WHERE controllingPower='\"{power}\"'"
        )

        if powerStates:
            powerStatesStr = ", ".join(
                list(map(lambda state: f"'\"{state}\"'", powerStates))
            )
            query += f" AND powerState IN ({powerStatesStr})"

        return self.__execute_powerplay_system_query(query)

    def get_unoccupied_powerplay_systems(self, power: str):
        query = (
            "SELECT controllingPower AS power, powerState, id64, name, coords, date, government, allegiance, factions, powers "
            f"FROM {self.table_name} "
            f"WHERE powerState='\"Unoccupied\"' AND EXISTS (SELECT 1 FROM json_each(powers) WHERE value = '{power}')"
        )
        return self.__execute_powerplay_system_query(query)

    def __execute_powerplay_system_query(self, query: str) -> List[PowerplaySystem]:
        with self.conn:
            cur = self.conn.execute(query)
            fetches = cur.fetchall()

            rows = []
            for fetch in fetches:
                rows.append(
                    self._convert_row_dict_to_dataclass_params(
                        self.powerplay_system_cols, fetch
                    )
                )

            return PowerplaySystem.schema().load(rows, many=True)
