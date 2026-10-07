from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base,sessionmaker
DATABASE_URL = "postgresql+psycopg://postgres:postgres123@localhost:5432/codeLense"
engine = create_engine(DATABASE_URL)
Base=declarative_base()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)