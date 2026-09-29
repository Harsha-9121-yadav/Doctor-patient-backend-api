from sqlalchemy import create_engine, event

from sqlalchemy.orm import sessionmaker, declarative_base

from config import settings


# =========================
# DATABASE ENGINE
# =========================

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}
)


# =========================
# ENABLE SQLITE FOREIGN KEYS
# =========================

if settings.DATABASE_URL.startswith("sqlite"):

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(dbapi_connection, connection_record):

        cursor = dbapi_connection.cursor()

        cursor.execute("PRAGMA foreign_keys=ON")

        cursor.close()


# =========================
# DATABASE SESSION
# =========================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# =========================
# BASE MODEL
# =========================

Base = declarative_base()


# =========================
# DATABASE DEPENDENCY
# =========================

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()