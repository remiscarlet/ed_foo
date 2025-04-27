from sqlalchemy.orm import Mapped, declarative_base

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True


class HasCoordinates(BaseModel):
    __abstract__ = True

    x: Mapped[float]
    y: Mapped[float]
    z: Mapped[float]
