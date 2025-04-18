import dataclasses
import json
import pprint
import sqlite3
from typing import Optional

from constants import DB_DATA_PATH
from ed_types import System
from timer import Timer


class SystemDB:
    table_name = "system"
    conn: sqlite3.Connection

    def __init__(self):
        timer = Timer("SystemDB.__init__()")

        self.conn = sqlite3.connect(DB_DATA_PATH)
        self.conn.row_factory = sqlite3.Row
        self.conn.isolation_level = None

        self.init_tables()

        timer.end()

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

        # print(
        #     query.format(
        #         table_name=system.db_table_name(),
        #         column_list=system.db_column_list(),
        #         quoted_and_comma_separated_values_list=system.db_values_list(),
        #     )
        # )
        timer = Timer()
        with self.conn:
            self.conn.execute(
                query.format(
                    table_name=system.db_table_name(),
                    column_list=system.db_column_list(),
                    quoted_and_comma_separated_values_list=system.db_values_list(),
                )
            )
        timer.end()

    def get_system(self, system_name: str) -> Optional[System]:
        timer = Timer()

        cur = None
        with self.conn:
            cur = self.conn.execute(
                f"SELECT * FROM {self.table_name} WHERE name='\"{system_name}\"'"
            )
        if cur is None:
            return None

        fetch = cur.fetchone()

        if fetch is None:
            return None

        cols = [field.name for field in dataclasses.fields(System)]
        params = {}
        for col in cols:
            col_val = fetch[col]
            if col_val is None:
                params[col] = None
            elif isinstance(col_val, int) or isinstance(col_val, float):
                params[col] = col_val
            else:
                params[col] = json.loads(col_val)

        timer.end()

        pprint.pprint(params, depth=2)
        system = System.schema().load(params)
        pprint.pprint(system, depth=2)
        return system