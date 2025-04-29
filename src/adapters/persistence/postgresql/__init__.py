from sqlalchemy.orm import DeclarativeBase, Mapped


class BaseModel(DeclarativeBase):
    __abstract__ = True
