from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """
    Manages application settings.
    Loads environment variables automatically from a .env file.
    """
    # Core Infrastructure
    DATABASE_URL: str = "sqlite:///sma_data.db"
    RABBITMQ_HOST: str = "localhost"

    # Jira Settings
    JIRA_SERVER: str = "https://your-jira-instance.atlassian.net"
    JIRA_USERNAME: str = "user@example.com"
    JIRA_API_TOKEN: str = "your_api_token"
    JIRA_PROJECT_KEY: str = "PROJ"

    # Git and GitHub Settings
    GIT_REPO_PATH: Optional[str] = None
    GIT_REPO_URL: Optional[str] = None
    GITHUB_TOKEN: Optional[str] = None

    # Bitbucket Settings
    BITBUCKET_SERVER: Optional[str] = None
    BITBUCKET_USERNAME: Optional[str] = None
    BITBUCKET_API_TOKEN: Optional[str] = None

    # Swarm Settings
    SWARM_SERVER: Optional[str] = None
    SWARM_USERNAME: Optional[str] = None
    SWARM_API_TOKEN: Optional[str] = None

    # Jenkins Settings
    JENKINS_HOST: Optional[str] = None
    JENKINS_USER: Optional[str] = None
    JENKINS_TOKEN: Optional[str] = None
    JENKINS_JOB_NAME: Optional[str] = None
    DEPLOYMENT_JOB_NAME_PATTERN: Optional[str] = None

    # SonarQube Settings
    SONARQUBE_HOST: Optional[str] = None
    SONARQUBE_TOKEN: Optional[str] = None
    SONARQUBE_PROJECT_KEY: Optional[str] = None

    # Local File Path Settings
    VTS_RESULTS_PATH: Optional[str] = None
    PROFILING_DATA_PATH: Optional[str] = None
    SURVEY_DATA_PATH: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()