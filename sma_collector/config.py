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

    # Bitbucket Settings
    BITBUCKET_SERVER: str = os.getenv("BITBUCKET_SERVER", "https://your-bitbucket-instance.com")
    BITBUCKET_USERNAME: str = os.getenv("BITBUCKET_USERNAME", "user@example.com")
    BITBUCKET_API_TOKEN: str = os.getenv("BITBUCKET_API_TOKEN", "your_api_token")

    # Swarm Settings
    SWARM_SERVER: str = os.getenv("SWARM_SERVER", "https://your-swarm-instance.com")
    SWARM_USERNAME: str = os.getenv("SWARM_USERNAME", "user@example.com")
    SWARM_API_TOKEN: str = os.getenv("SWARM_API_TOKEN", "your_api_token")

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///sma_data.db")

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()


