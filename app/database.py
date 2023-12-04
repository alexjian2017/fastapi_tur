import time

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase
import psycopg2
from psycopg2.extras import RealDictCursor

from .config import settings


SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = declarative_base()


class Base(DeclarativeBase):
    pass


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# while 1:
#     try:
#         con = psycopg2.connect(host='localhost', database='fastapi', user='postgres',
#                                password='12345678a', cursor_factory=RealDictCursor)
#         cursor = con.cursor()
#         print('Connecting to Database successfully')
#         break
#     except Exception as e:
#         print(f'Connecting to Database failed {e}')
#         time.sleep(5)
