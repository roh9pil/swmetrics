from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# API 응답/요청에 사용될 데이터 모델(스키마)을 정의합니다.
# SQLAlchemy 모델과 분리하여 API의 데이터 형태를 명확히 합니다.

class Commit(BaseModel):
    hash: str
    author_name: str
    author_email: str
    authored_datetime: datetime
    message: Optional[str] = None
    lines_added: int
    lines_deleted: int
    files_changed: int

    class Config:
        from_attributes = True # SQLAlchemy 모델 객체를 Pydantic 모델로 자동 변환

class Issue(BaseModel):
    key: str
    summary: str
    description: Optional[str] = None
    status: Optional[str] = None
    issue_type: Optional[str] = None
    reporter: Optional[str] = None
    assignee: Optional[str] = None
    created: datetime
    updated: Optional[datetime] = None
    resolved: Optional[datetime] = None

    class Config:
        from_attributes = True

