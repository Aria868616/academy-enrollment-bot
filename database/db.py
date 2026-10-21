"""Database engine and table creation."""
from sqlmodel import SQLModel, create_engine

from config import DB_NAME
from database import models  # noqa: F401  (registers the tables on SQLModel.metadata)

engine = create_engine(DB_NAME, echo=False)


def create_db_and_tables() -> None:
    """Create all tables that do not exist yet."""
    SQLModel.metadata.create_all(engine)