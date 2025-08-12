from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Commit(Base):
    __tablename__ = 'commits'
    hash = Column(String(40), primary_key=True)
    author_name = Column(String(100), nullable=False)
    author_email = Column(String(100), nullable=False)
    authored_datetime = Column(DateTime, nullable=False)
    committer_name = Column(String(100), nullable=False)
    committer_email = Column(String(100), nullable=False)
    committed_datetime = Column(DateTime, nullable=False)
    message = Column(Text, nullable=True)
    lines_added = Column(Integer, default=0)
    lines_deleted = Column(Integer, default=0)
    files_changed = Column(Integer, default=0)

class Issue(Base):
    __tablename__ = 'issues'
    key = Column(String(20), primary_key=True)
    summary = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50))
    issue_type = Column(String(50))
    reporter = Column(String(100))
    assignee = Column(String(100), nullable=True)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime, nullable=True)
    resolved = Column(DateTime, nullable=True)

