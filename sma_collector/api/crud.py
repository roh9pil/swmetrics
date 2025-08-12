from sqlalchemy.orm import Session
from sma_collector.models import models

def get_commits(db: Session, skip: int = 0, limit: int = 100):
    """
    데이터베이스에서 커밋 목록을 조회합니다.
    """
    return db.query(models.Commit).offset(skip).limit(limit).all()

def get_issues(db: Session, skip: int = 0, limit: int = 100):
    """
    데이터베이스에서 이슈 목록을 조회합니다.
    """
    return db.query(models.Issue).offset(skip).limit(limit).all()

def get_issue_by_key(db: Session, issue_key: str):
    """
    키를 기준으로 특정 이슈를 조회합니다.
    """
    return db.query(models.Issue).filter(models.Issue.key == issue_key).first()

