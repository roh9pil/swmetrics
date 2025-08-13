from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """
    애플리케이션 설정을 관리하는 클래스입니다.
    .env 파일에서 환경 변수를 자동으로 로드합니다.
    """
    # Jira Settings
    JIRA_SERVER: str = "https://your-jira-instance.atlassian.net"
    JIRA_USERNAME: str = "user@example.com"
    JIRA_API_TOKEN: str = "your_api_token"
    JIRA_PROJECT_KEY: str = "PROJ"

    # Git and GitHub Settings
    GIT_REPO_PATH: str = "./local_repo"
    GIT_REPO_URL: Optional[str] = None
    GITHUB_TOKEN: Optional[str] = None

    # Bitbucket Settings
    BITBUCKET_SERVER: str = "https://your-bitbucket-instance.com"
    BITBUCKET_USERNAME: str = "user@example.com"
    BITBUCKET_API_TOKEN: str = "your_api_token"

    # Swarm Settings
    SWARM_SERVER: str = "https://your-swarm-instance.com"
    SWARM_USERNAME: str = "user@example.com"
    SWARM_API_TOKEN: str = "your_api_token"

    # Database URL
    DATABASE_URL: str = "sqlite:///sma_data.db"

    # RabbitMQ Host
    RABBITMQ_HOST: str = "rabbitmq"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()