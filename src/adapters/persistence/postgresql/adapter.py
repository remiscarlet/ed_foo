import pprint
from typing import List

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import DeclarativeMeta, Session

from src.adapters.persistence.postgresql import SessionLocal
from src.adapters.persistence.postgresql.db import SystemsDB
from src.core.models.system_model import System
from src.core.ports.system_port import SystemPort


def upsert_all(
    session: Session,
    model: DeclarativeMeta,
    objects: list,
    conflict_cols: list[str],
    exclude_update_cols: list[str] = [],
):
    if not objects:
        return

    rows = [model.from_core_model_to_dict(obj) for obj in objects]
    pprint.pprint(rows[:2])

    updatable_cols = [
        col.name
        for col in model.__table__.columns
        if col.name not in conflict_cols and col.name not in exclude_update_cols
    ]

    stmt = (
        pg_insert(model)
        .values(rows)
        .on_conflict_do_update(
            index_elements=conflict_cols, set_={col: getattr(pg_insert(model).excluded, col) for col in updatable_cols}
        )
    )

    print(str(stmt))
    session.execute(stmt)


class SystemsAdapter(SystemPort):
    def __init__(self) -> None:
        self.session = SessionLocal()

    def upsert_systems(self, systems: List[System]) -> None:
        upsert_all(self.session, SystemsDB, systems, conflict_cols=["id", "name"], exclude_update_cols=[])

    def get_system(self, system_name: str) -> System:
        query = select(SystemsDB).where(SystemsDB.name.is_(system_name))
        db_system = self.session.scalars(query).first()
        if not db_system:
            raise Exception("System not found")
        return db_system.to_core_model()

    def delete_system(self, system_name: str) -> None:
        pass
