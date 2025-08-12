import os
import logging
from sqlalchemy import create_engine, Column, String, DateTime, Integer, BigInteger, ForeignKey, Float, Date
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.dialects.postgresql import insert
from..config import settings

Base = declarative_base()

# --- Phase 1 Models ---
class Commit(Base):
    __tablename__ = 'commits'
    sha = Column(String(40), primary_key=True)
    author_name = Column(String(255))
    author_email = Column(String(255))
    authored_date = Column(DateTime(timezone=True))
    message = Column(String)

class Issue(Base):
    __tablename__ = 'issues'
    id = Column(String(255), primary_key=True)
    issue_key = Column(String(255), unique=True)
    type = Column(String(100))
    status = Column(String(100))
    title = Column(String)
    created_date = Column(DateTime(timezone=True))
    resolved_date = Column(DateTime(timezone=True), nullable=True)
    lead_time_minutes = Column(Integer, nullable=True)
    sli = Column(Integer, nullable=True) # Phase 2 addition

class Build(Base):
    __tablename__ = 'builds'
    id = Column(String(255), primary_key=True)
    job_name = Column(String(255))
    number = Column(Integer)
    status = Column(String(100))
    start_time = Column(DateTime(timezone=True))
    finish_time = Column(DateTime(timezone=True))
    duration_millis = Column(BigInteger)
    commits = relationship("BuildCommit", back_populates="build")

class BuildCommit(Base):
    __tablename__ = 'build_commits'
    build_id = Column(String(255), ForeignKey('builds.id'), primary_key=True)
    commit_sha = Column(String(40), ForeignKey('commits.sha'), primary_key=True)
    build = relationship("Build", back_populates="commits")

class Deployment(Base):
    __tablename__ = 'deployments'
    id = Column(String(255), ForeignKey('builds.id'), primary_key=True)
    commit_sha = Column(String(40), nullable=True)
    start_time = Column(DateTime(timezone=True))
    finish_time = Column(DateTime(timezone=True))

class Incident(Base):
    __tablename__ = 'incidents'
    id = Column(String(255), ForeignKey('issues.id'), primary_key=True)
    deployment_id = Column(String(255), ForeignKey('deployments.id'), nullable=True)
    created_date = Column(DateTime(timezone=True))
    resolved_date = Column(DateTime(timezone=True), nullable=True)

# --- Phase 2 Models ---
class VtsRun(Base):
    __tablename__ = 'vts_runs'
    id = Column(String(255), primary_key=True)
    run_name = Column(String(255))
    test_plan = Column(String(255))
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))
    total_tests = Column(Integer)
    passed_tests = Column(Integer)
    failed_tests = Column(Integer)
    pass_rate = Column(Float)

class OspMetric(Base):
    __tablename__ = 'osp_metrics'
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True))
    device_id = Column(String(255))
    metric_name = Column(String(255))
    metric_value = Column(Float)
    source = Column(String(255))

# --- Phase 3 Models ---
class TeamSurvey(Base):
    __tablename__ = 'team_surveys'
    id = Column(Integer, primary_key=True, autoincrement=True)
    survey_date = Column(Date, nullable=False)
    team_name = Column(String(255), nullable=False)
    satisfaction_score = Column(Float)

class CodeReview(Base):
    __tablename__ = 'code_reviews'
    id = Column(String(255), primary_key=True)
    repo_name = Column(String(255))
    pr_number = Column(Integer)
    title = Column(String)
    author = Column(String(255))
    created_date = Column(DateTime(timezone=True))
    merged_date = Column(DateTime(timezone=True), nullable=True)
    first_comment_date = Column(DateTime(timezone=True), nullable=True)
    time_to_first_review_minutes = Column(Integer, nullable=True)
    time_to_merge_minutes = Column(Integer, nullable=True)
    comment_count = Column(Integer)

class CodeQualityMetric(Base):
    __tablename__ = 'code_quality_metrics'
    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_date = Column(Date, nullable=False)
    project_key = Column(String(255), nullable=False)
    metric_name = Column(String(255), nullable=False)
    metric_value = Column(Float)

# --- Database Session Management ---
engine = create_engine(settings.DB_SOURCE)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_session():
    return SessionLocal()

def bulk_upsert(session, model, records: list[dict]):
    if not records:
        return
    
    table = model.__table__
    stmt = insert(table).values(records)
    
    primary_keys = [key.name for key in table.primary_key]
    update_cols = {
        col.name: col for col in stmt.excluded if not col.primary_key
    }
    
    if not primary_keys:
        logging.warning(f"Model {model.__name__} has no primary key for upsert. Skipping.")
        return

    if update_cols:
        stmt = stmt.on_conflict_do_update(
            index_elements=primary_keys,
            set_=update_cols
        )
    else:
        stmt = stmt.on_conflict_do_nothing(index_elements=primary_keys)

    session.execute(stmt)
    session.commit()

