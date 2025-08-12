from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """
    애플리케이션 설정을 관리하는 클래스입니다.
    """
    JIRA_SERVER: str = os.getenv("JIRA_SERVER", "https://your-jira-instance.atlassian.net")
    JIRA_USERNAME: str = os.getenv("JIRA_USERNAME", "user@example.com")
    JIRA_API_TOKEN: str = os.getenv("JIRA_API_TOKEN", "your_api_token")
    JIRA_PROJECT_KEY: str = os.getenv("JIRA_PROJECT_KEY", "PROJ")

    GIT_REPO_PATH: str = os.getenv("GIT_REPO_PATH", "./local_repo")

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///sma_data.db")

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()


