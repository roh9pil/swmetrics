from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from sma_collector.storage.db import Database
from . import crud, schemas

app = FastAPI(
    title="Software Metrics Analyzer API",
    description="API for accessing collected Git and Jira data.",
    version="1.0.0"
)

# 데이터베이스 의존성 주입 함수
def get_db_session():
    db = Database()
    with db.get_session() as session:
        yield session

@app.get("/")
def read_root():
    return {"message": "Welcome to the Software Metrics Analyzer API"}

@app.get("/commits/", response_model=List[schemas.Commit])
def read_commits(skip: int = 0, limit: int = 100, db: Session = Depends(get_db_session)):
    """
    저장된 Git 커밋 목록을 조회합니다.
    """
    commits = crud.get_commits(db, skip=skip, limit=limit)
    return commits

@app.get("/issues/", response_model=List[schemas.Issue])
def read_issues(skip: int = 0, limit: int = 100, db: Session = Depends(get_db_session)):
    """
    저장된 Jira 이슈 목록을 조회합니다.
    """
    issues = crud.get_issues(db, skip=skip, limit=limit)
    return issues

@app.get("/issues/{issue_key}", response_model=schemas.Issue)
def read_issue(issue_key: str, db: Session = Depends(get_db_session)):
    """
    특정 키(key)를 가진 Jira 이슈를 조회합니다.
    """
    db_issue = crud.get_issue_by_key(db, issue_key=issue_key)
    if db_issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")
    return db_issue

