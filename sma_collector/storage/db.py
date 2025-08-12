import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from sma_collector.config import settings
from sma_collector.models.models import Base

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_url: str = settings.DATABASE_URL):
        self.engine = create_engine(db_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def init_db(self):
        Base.metadata.create_all(bind=self.engine)

    @contextmanager
    def get_session(self) -> Session:
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()

