import logging
from git import Repo, GitCommandError, NoSuchPathError
from github import Github, GithubException
from sma_collector.config import settings
from .collector import BaseCollector

logger = logging.getLogger(__name__)

class GitConnector(BaseCollector):
    """
    로컬 Git 레포지토리와 GitHub에서 데이터를 수집하는 클래스.
    """
    def __init__(self, repo_path: str, repo_url: str = None, github_token: str = None):
        self.repo_path = repo_path
        self.repo_url = repo_url
        self.github_token = github_token
        self._repo = self._clone_or_open_repo()

        self.github_client = Github(github_token) if github_token else None
        self.github_repo_name = self._get_github_repo_name(repo_url) if repo_url else None

    def _get_github_repo_name(self, repo_url: str) -> str | None:
        """Extracts 'owner/repo' from a GitHub URL."""
        if "github.com" in repo_url:
            return '/'.join(repo_url.split('/')[-2:]).replace('.git', '')
        return None

    def _clone_or_open_repo(self) -> Repo | None:
        """로컬 레포지토리를 열거나, 없으면 원격 URL에서 클론합니다."""
        try:
            repo = Repo(self.repo_path)
            logger.info(f"Repository found at {self.repo_path}.")
            if self.repo_url:
                 logger.info("Pulling latest changes.")
                 repo.remotes.origin.pull()
        except (NoSuchPathError, IndexError):
            if not self.repo_url:
                logger.error("Repository not found at specified path and no remote URL provided.")
                return None
            logger.info(f"Repository not found, cloning from {self.repo_url}")
            try:
                repo = Repo.clone_from(self.repo_url, self.repo_path)
            except GitCommandError as e:
                logger.error(f"Failed to clone repository: {e}")
                return None
        except GitCommandError as e:
            logger.error(f"Error pulling latest changes: {e}")
            # Continue with the local version
            repo = Repo(self.repo_path)

        return repo

    def collect(self) -> list[dict]:
        """Git과 GitHub에서 데이터를 수집합니다."""
        if not self._repo:
            return []

        commits = self.collect_commits()
        pull_requests = self.collect_pull_requests()

        # In a real scenario, you might want to merge or relate this data.
        # For now, we can return them as separate entries or focus on one.
        # Let's assume for now the goal is to get commits.
        # This can be expanded later.
        return commits

    def collect_commits(self, max_count: int = 1000) -> list[dict]:
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

    def collect_pull_requests(self, max_count: int = 100) -> list[dict]:
        """GitHub에서 Pull Request 목록을 수집합니다."""
        reviews = []
        if not self.github_client or not self.github_repo_name:
            logger.warning("GitHub client or repo name not configured. Skipping PR collection.")
            return reviews

        try:
            repo = self.github_client.get_repo(self.github_repo_name)
            pulls = repo.get_pulls(state='all', sort='created', direction='desc')
            
            for pr in pulls[:max_count]:
                # This part can be complex due to how reviews and comments are fetched.
                # Simplified for this example.
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
