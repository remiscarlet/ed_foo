from typing import List

from sqlalchemy import select

from src.adapters.persistence.postgresql import SessionLocal
from src.adapters.persistence.postgresql.db import SystemsDB
from src.core.models.system_model import System
from src.core.ports.system_port import SystemPort


class SystemsAdapter(SystemPort):
    def __init__(self) -> None:
        self.session = SessionLocal()

    def upsert_systems(self, systems: List[System]) -> None:
        pass

    def get_system(self, system_name: str) -> System:
        query = select(SystemsDB).where(SystemsDB.name.is_(system_name))
        db_system = self.session.scalars(query).first()
        if not db_system:
            raise Exception("System not found")
        return db_system.to_core_model()

    def delete_system(self, system_name: str) -> None:
        pass
