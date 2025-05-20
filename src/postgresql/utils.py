from typing import Any, Type

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from src.common.logging import get_logger
from src.postgresql import BaseModel

logger = get_logger(__name__)


def upsert_all[T: BaseModel](
    session: Session,
    model: Type[T],
    rows: list[dict[str, Any]],
    exclude_update_cols: list[str] | None = None,
    debug_print_extra_cols: list[str] | None = None,
) -> list[T]:
    """Upserts a list of dicts representing sqlalchemy objects"""
    if not rows:
        return []
    debug_print_extra_cols = debug_print_extra_cols or []
    exclude_update_cols = exclude_update_cols or []
    exclude_update_cols.append("id")  # Never update id column

    conflict_cols = list(model.unique_columns)
    cols_to_print = conflict_cols + debug_print_extra_cols
    logger.debug(f"{len(rows)} {model.__name__} items being upserted...")
    logger.trace(repr([{k: v for k, v in item.items() if k in cols_to_print} for item in rows]))

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

    results = session.scalars(stmt.returning(model), execution_options={"populate_existing": True})
    session.commit()

    return list(iter(results.all()))
