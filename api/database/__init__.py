from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from api.config import DATABASE_URL

engine = create_engine(f'sqlite:///{DATABASE_URL}', connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

TABLES = ['case_ids', 'collisions', 'parties', 'victims']


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
