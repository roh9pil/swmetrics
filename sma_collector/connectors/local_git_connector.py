import logging
from typing import List, Dict, Any, Optional
from git import Repo, GitCommandError, NoSuchPathError
from sma_collector.config import Settings
from .collector import BaseCollector

logger = logging.getLogger(__name__)

class LocalGitConnector(BaseCollector):
    """
    로컬 Git 레포지토리에서 데이터를 수집하는 클래스.
    """
    def __init__(self, settings: Settings):
        self.settings = settings
        self._repo = self._clone_or_open_repo()

    def _clone_or_open_repo(self) -> Optional[Repo]:
        """로컬 레포지토리를 열거나, 없으면 원격 URL에서 클론합니다."""
        try:
            repo = Repo(self.settings.GIT_REPO_PATH)
            logger.info(f"Repository found at {self.settings.GIT_REPO_PATH}.")
            if self.settings.GIT_REPO_URL:
                logger.info("Pulling latest changes.")
                repo.remotes.origin.pull()
        except (NoSuchPathError, IndexError):
            if not self.settings.GIT_REPO_URL:
                logger.error("Repository not found at specified path and no remote URL provided.")
                return None
            logger.info(f"Repository not found, cloning from {self.settings.GIT_REPO_URL}")
            try:
                repo = Repo.clone_from(self.settings.GIT_REPO_URL, self.settings.GIT_REPO_PATH)
            except GitCommandError as e:
                logger.error(f"Failed to clone repository: {e}")
                return None
        except GitCommandError as e:
            logger.error(f"Error pulling latest changes: {e}")
            repo = Repo(self.settings.GIT_REPO_PATH)

        return repo

    def collect(self, max_count: int = 1000) -> List[Dict[str, Any]]:
        """지정된 브랜치에서 커밋 목록을 수집합니다."""
        commits = []
        if not self._repo:
            return commits

        try:
            for commit in self._repo.iter_commits('HEAD', max_count=max_count):
                commits.append({
                    "sha": commit.hexsha,
                    "author_name": commit.author.name,
                    "author_email": commit.author.email,
                    "authored_date": commit.authored_datetime,
                    "message": commit.message.strip(),
                })
            logger.info(f"Collected {len(commits)} commits.")
        except GitCommandError as e:
            logger.error(f"Error collecting commits: {e}")

        return commits
