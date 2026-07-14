from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Using SQLite for simplicity, as the plan notes. To switch to
# PostgreSQL, just change this URL, e.g.:
#   DATABASE_URL = "postgresql://user:pass@localhost/taskdb"
# and pip install psycopg2-binary - nothing else in this file changes.
DATABASE_URL = "sqlite:///./task_api.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
