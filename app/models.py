from sqlalchemy import Column, Integer, Text, DateTime
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

from app.database import Base


class Repository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True)
    github_url = Column(Text, nullable=False)
    local_path = Column(Text)
    status = Column(Text, default="PROCESSING")

    files_processed = Column(Integer, default=0)
    chunks_created = Column(Integer, default=0)

    embedding_batches_processed = Column(Integer, default=0)
    total_embedding_batches = Column(Integer, default=0)

    created_at = Column(DateTime, server_default=func.now())

    latest_commit = Column(Text)
    
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