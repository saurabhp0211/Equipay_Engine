from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()
# SQLALCHEMY_DATABASE_URL = "sqlite:///./expenses.db"
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
if not SQLALCHEMY_DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set")



engine=create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal=sessionmaker(autocommit=False, autoflush=False, bind=engine)

# @event.listens_for(Engine,"connect")
# def set_sqlite_pragma(dbapi_connection, connection_record):
#     cursor=dbapi_connection.cursor()
#     cursor.execute("PRAGMA foreign_keys=ON")
#     cursor.close()

Base=declarative_base()

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally: 
        db.close()