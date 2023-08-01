from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


@lru_cache(None)
def create_engine(path: str):
    # TODO: use path
    engine = create_engine(f"sqlite://", echo=True)
    Base.metadata.create_all(engine)
    return engine
