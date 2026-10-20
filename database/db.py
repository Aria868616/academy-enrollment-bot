"""Database engine and table creation."""
from sqlmodel import Session, SQLModel, create_engine

from config import DB_NAME
from database import models  # noqa: F401  (registers the tables on SQLModel.metadata)

engine = create_engine(DB_NAME, echo=False)


def create_db_and_tables() -> None:
    """Create all tables that do not exist yet."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Yield a database session and close it afterwards."""
    with Session(engine) as session:
        yield session