import logging
from typing import List, Dict, Any, Optional
from github import Github, GithubException
from sma_collector.config import Settings
from .collector import BaseCollector

logger = logging.getLogger(__name__)

class GitHubConnector(BaseCollector):
    """
    GitHub에서 Pull Request 데이터를 수집하는 클래스.
    """
    def __init__(self, settings: Settings):
        self.settings = settings
        self.github_client = self._get_client()
        self.github_repo_name = self._get_github_repo_name(self.settings.GIT_REPO_URL)

    def _get_client(self) -> Optional[Github]:
        """GitHub 클라이언트를 생성합니다."""
        if not self.settings.GITHUB_TOKEN:
            logger.warning("GitHub token not provided. Skipping GitHub client creation.")
            return None
        try:
            return Github(self.settings.GITHUB_TOKEN)
        except Exception as e:
            logger.error(f"Failed to create GitHub client: {e}")
            return None

    def _get_github_repo_name(self, repo_url: Optional[str]) -> Optional[str]:
        """GitHub URL에서 'owner/repo'를 추출합니다."""
        if repo_url and "github.com" in repo_url:
            return '/'.join(repo_url.split('/')[-2:]).replace('.git', '')
        return None

    def collect(self, max_count: int = 100) -> List[Dict[str, Any]]:
        """GitHub에서 Pull Request 목록을 수집합니다."""
        reviews = []
        if not self.github_client or not self.github_repo_name:
            logger.warning("GitHub client or repo name not configured. Skipping PR collection.")
            return reviews

        try:
            repo = self.github_client.get_repo(self.github_repo_name)
            pulls = repo.get_pulls(state='all', sort='created', direction='desc')
            
            for pr in pulls[:max_count]:
                reviews.append({
                    "id": f"{repo.id}-{pr.number}",
                    "repo_name": self.github_repo_name,
                    "pr_number": pr.number,
                    "title": pr.title,
                    "author": pr.user.login,
                    "created_date": pr.created_at,
                    "merged_date": pr.merged_at,
                    "state": pr.state,
                })
            logger.info(f"Collected {len(reviews)} pull requests from GitHub.")
        except GithubException as e:
            logger.error(f"Failed to collect GitHub pull requests: {e}")

        return reviews
