from datetime import datetime
from typing import Any, Optional

from gen.eddn_models import fsssignaldiscovered_v1_0
from sqlalchemy import (
    ARRAY,
    BigInteger,
    Boolean,
    DateTime,
    Float,
    Integer,
    PrimaryKeyConstraint,
    SmallInteger,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, TEXT
from sqlalchemy.orm import Mapped, mapped_column

from src.common.game_constants import get_symbol_by_eddn_name
from src.common.logging import get_logger
from src.postgresql import BaseModel

logger = get_logger(__name__)


class SignalsTimeseries(BaseModel):
    # This models the EDDN fsssignaldiscovered-v1.0's Signals object shape
    #   (gen.eddn_models.fsssignaldiscovered_v1_0.Signal)
    # Note: EDDN mandates the 'time_remaining' field MUST NOT be present (Can be PII)
    unique_columns = ("id", "timestamp")
    __tablename__ = "signals"
    __table_args__ = (
        PrimaryKeyConstraint("id", "timestamp"),
        {"schema": "timescaledb"},
    )

    id: Mapped[int] = mapped_column(Integer, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)

    system_id: Mapped[int] = mapped_column(Integer, nullable=False)

    signal_type: Mapped[Optional[str]] = mapped_column(TEXT)
    signal_name: Mapped[Optional[str]] = mapped_column(TEXT)

    is_station: Mapped[Optional[bool]] = mapped_column(Boolean)
    uss_type: Mapped[Optional[str]] = mapped_column(TEXT)

    spawning_state: Mapped[Optional[str]] = mapped_column(TEXT)
    spawning_faction: Mapped[Optional[str]] = mapped_column(TEXT)
    spawning_power: Mapped[Optional[str]] = mapped_column(TEXT)
    opposing_power: Mapped[Optional[str]] = mapped_column(TEXT)

    threat_level: Mapped[Optional[int]] = mapped_column(SmallInteger)

    fields = [
        "id",
        "signal_type",
        "signal_name",
        "is_station",
        "uss_type",
        "spawning_state",
        "spawning_faction",
        "spawning_power",
        "opposing_power",
        "threat_level",
    ]

    @staticmethod
    def to_dicts_from_fsssignaldiscovered_v1_0(
        model: fsssignaldiscovered_v1_0.Model, system_id: int
    ) -> list[dict[str, Any]]:
        dicts = []
        for signal in model.message.signals:
            signal_name = get_symbol_by_eddn_name(signal.SignalName) or signal.SignalName
            if signal_name[0] == "$":
                logger.warning(
                    "Encountered dollarstring SignalName we didn't know about! "
                    f"Skipping signal... '{signal.SignalName}'"
                )
                continue

            uss_type = None
            if signal.USSType is not None:
                uss_type = get_symbol_by_eddn_name(signal.USSType) or signal.USSType

            if uss_type is not None and uss_type[0] == "$":
                logger.warning(
                    "Encountered dollarstring USSType we didn't know about! " f"Skipping signal... '{signal.USSType}'"
                )
                continue

            spawning_state = None
            if signal.SpawningState is not None:
                spawning_state = get_symbol_by_eddn_name(signal.SpawningState) or signal.SpawningState
            if spawning_state is not None and spawning_state[0] == "$":
                logger.warning(
                    "Encountered dollarstring SpawningState we didn't know about! "
                    f"Skipping signal... '{signal.SpawningState}'"
                )
                continue

            dicts.append(
                {
                    "system_id": system_id,
                    "timestamp": signal.timestamp,
                    "signal_type": signal.SignalType,
                    "signal_name": signal_name,
                    "is_station": signal.IsStation,
                    "uss_type": uss_type,
                    "spawning_state": spawning_state,
                    "spawning_faction": signal.SpawningFaction,
                    "spawning_power": signal.SpawningPower,
                    "opposing_power": signal.OpposingPower,
                    "threat_level": signal.ThreatLevel,
                }
            )
        return dicts

    def __repr__(self) -> str:
        non_none_fields = []
        for field in self.fields:
            val = getattr(self, field)
            if val is not None:
                if isinstance(val, str):
                    val = f'"{val}"'
                non_none_fields.append(f"{field}={val}")

        return f"<SignalsTimeseries({', '.join(non_none_fields)})>"


class FactionPresencesTimeseries(BaseModel):
    # This models timeseries-interesting fields from the core.faction_presences table
    __tablename__ = "faction_presences"
    __table_args__ = (
        PrimaryKeyConstraint("id", "timestamp"),
        {"schema": "timescaledb"},
    )

    id: Mapped[int] = mapped_column(Integer)
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)

    system_id: Mapped[int] = mapped_column(Integer, nullable=False)
    faction_id: Mapped[int] = mapped_column(Integer, nullable=False)

    influence: Mapped[Optional[float]] = mapped_column(Float)
    state: Mapped[Optional[str]] = mapped_column(Text)
    happiness: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    active_states: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text))
    pending_states: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text))
    recovering_states: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text))

    def __repr__(self) -> str:
        return f"<FactionPresencesTimeseries(id={self.id}, system_id={self.system_id}, faction_id={self.faction_id})>"


class SystemsTimeseries(BaseModel):
    # This models timeseries-interesting fields from the core.systems table
    __tablename__ = "systems"
    __table_args__ = (
        PrimaryKeyConstraint("id", "timestamp"),
        {"schema": "timescaledb"},
    )

    id: Mapped[int] = mapped_column(Integer)
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)

    allegiance: Mapped[Optional[str]] = mapped_column(Text)
    population: Mapped[Optional[int]] = mapped_column(BigInteger)
    primary_economy: Mapped[Optional[str]] = mapped_column(Text)
    secondary_economy: Mapped[Optional[str]] = mapped_column(Text)
    security: Mapped[Optional[str]] = mapped_column(Text)
    government: Mapped[Optional[str]] = mapped_column(Text)

    controlling_faction_id: Mapped[Optional[int]] = mapped_column(Integer)

    controlling_power: Mapped[Optional[str]] = mapped_column(Text)
    power_conflict_progress: Mapped[Optional[list[dict[str, float]]]] = mapped_column(JSONB)
    power_state: Mapped[Optional[str]] = mapped_column(Text)
    power_state_control_progress: Mapped[Optional[float]] = mapped_column(Float)
    power_state_reinforcement: Mapped[Optional[float]] = mapped_column(Float)
    power_state_undermining: Mapped[Optional[float]] = mapped_column(Float)
    powers: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text))

    def __repr__(self) -> str:
        return f"<SystemsTimeseries(id={self.id}, name={self.name})>"
