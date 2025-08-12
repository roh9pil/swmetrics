import os
from pydantic import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    DB_SOURCE: str
    
    # Phase 1
    GIT_REPO_URL: str
    JIRA_HOST: str
    JIRA_USER: str
    JIRA_TOKEN: str
    JIRA_PROJECT_KEY: str
    JENKINS_HOST: str
    JENKINS_USER: str
    JENKINS_TOKEN: str
    JENKINS_JOB_NAME: str
    DEPLOYMENT_JOB_NAME_PATTERN: str
    
    # Phase 2
    VTS_RESULTS_PATH: str = "/app/data/vts_results"
    PROFILING_DATA_PATH: str = "/app/data/profiling"
    
    # Phase 3
    GITHUB_TOKEN: str | None = None
    SURVEY_DATA_PATH: str = "/app/data/surveys/survey.csv"
    SONARQUBE_HOST: str | None = None
    SONARQUBE_TOKEN: str | None = None
    SONARQUBE_PROJECT_KEY: str | None = None

settings = Settings()

