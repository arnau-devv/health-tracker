
from .config import DB_URL
from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Engine handles the physical connection to the DB.
# [Setting echo=True would log all generated SQL queries to the console.]
# check_same_thread=False avoids thread errors when interacting with WebSockets or Electron
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})

# Automatically enables foreign keys and WAL performance mode in SQLite.
# # Enables WAL mode: allows concurrent reads and writes without locking the database.
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.close()
    
# Session is a factory (template) for database transactions.
# Each time a database operation is required, an instance should be created.
# Usage: with Session() as session: ...
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# DeclarativeBase is the parent class for all ORM models.
# It serves as a registry, allowing SQLAlchemy to track all defined tables.
# All domain models must inherit from this class.
class Base(DeclarativeBase):
    pass


def init_db():
    """Crea todas las tablas definidas en los modelos ORM que hereden de Base."""
    print(f"DATABASE URL -> {DB_URL}")
    Base.metadata.create_all(bind=engine)