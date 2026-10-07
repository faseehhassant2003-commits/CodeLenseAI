from sqlalchemy import Column, Integer, Text, DateTime
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

from app.database import Base


class Repository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True)
    github_url = Column(Text, nullable=False)
    local_path = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

class CodeChunk(Base):
    __tablename__ = "code_chunks"

    id = Column(Integer, primary_key=True)
    repository_id = Column(Integer, nullable=False)
    file_path = Column(Text, nullable=False)
    language = Column(Text)
    chunk_index = Column(Integer)

    start_line = Column(Integer)
    end_line = Column(Integer)

    content = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    embedding = Column(Vector(384))