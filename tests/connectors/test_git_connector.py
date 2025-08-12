import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from git import Repo, GitCommandError, NoSuchPathError
from github import Github, GithubException
from sma_collector.connectors.git_connector import GitConnector
import datetime

@pytest.fixture
def mock_git_repo(mocker):
    """Mocks the git.Repo object."""
    mock_repo = MagicMock(spec=Repo)

    # Mock commits
    mock_commit = MagicMock()
    mock_commit.hexsha = '12345'
    mock_commit.author.name = 'Test Author'
    mock_commit.author.email = 'author@test.com'
    mock_commit.authored_datetime = datetime.datetime.now()
    mock_commit.message = 'Test commit message'

    mock_repo.iter_commits.return_value = [mock_commit]

    # Patch the Repo class to return our mock
    mocker.patch('sma_collector.connectors.git_connector.Repo', return_value=mock_repo)
    return mock_repo

@pytest.fixture
def mock_github_client(mocker):
    """Mocks the github.Github client."""
    mock_github = MagicMock(spec=Github)

    # Mock GitHub repo and PRs
    mock_gh_repo = MagicMock()
    mock_gh_repo.id = 100

    mock_pr = MagicMock()
    mock_pr.number = 1
    mock_pr.title = 'Test PR'
    mock_pr.user.login = 'pr_author'
    mock_pr.created_at = datetime.datetime.now()
    mock_pr.merged_at = None
    mock_pr.state = 'open'

    mock_gh_repo.get_pulls.return_value = [mock_pr]
    mock_github.get_repo.return_value = mock_gh_repo

    mocker.patch('sma_collector.connectors.git_connector.Github', return_value=mock_github)
    return mock_github

def test_git_connector_existing_repo(mock_git_repo, mocker):
    """Test initialization with an existing local repository."""
    mocker.patch('git.Repo', return_value=mock_git_repo)

    connector = GitConnector(repo_path='/fake/path')

    assert connector._repo is not None
    mock_git_repo.remotes.origin.pull.assert_not_called() # No URL, no pull

def test_git_connector_clone_repo(mocker):
    """Test initialization that clones a repository."""
    # When Repo(path) is called, raise NoSuchPathError
    mocker.patch('sma_collector.connectors.git_connector.Repo.__init__', side_effect=NoSuchPathError, return_value=None)

    # Patch the clone_from method to check its call
    mock_repo_instance = MagicMock(spec=Repo)
    mock_clone_from = mocker.patch('sma_collector.connectors.git_connector.Repo.clone_from', return_value=mock_repo_instance)

    connector = GitConnector(repo_path='/fake/path', repo_url='https://github.com/user/repo.git')

    mock_clone_from.assert_called_once_with('https://github.com/user/repo.git', '/fake/path')
    assert connector._repo == mock_repo_instance

def test_collect_commits_success(mock_git_repo):
    """Test successful collection of commits."""
    connector = GitConnector(repo_path='/fake/path')
    connector._repo = mock_git_repo # Ensure it uses the mock

    commits = connector.collect_commits()

    assert len(commits) == 1
    assert commits[0]['sha'] == '12345'
    assert commits[0]['author_name'] == 'Test Author'

def test_collect_commits_error(mock_git_repo):
    """Test handling of errors during commit collection."""
    mock_git_repo.iter_commits.side_effect = GitCommandError('git', 'failed')

    connector = GitConnector(repo_path='/fake/path')
    connector._repo = mock_git_repo

    commits = connector.collect_commits()

    assert len(commits) == 0

def test_collect_pull_requests_success(mock_github_client):
    """Test successful collection of pull requests."""
    connector = GitConnector(
        repo_path='/fake/path',
        repo_url='https://github.com/user/repo.git',
        github_token='fake_token'
    )

    prs = connector.collect_pull_requests()

    assert len(prs) == 1
    assert prs[0]['pr_number'] == 1
    assert prs[0]['author'] == 'pr_author'
    mock_github_client.get_repo.assert_called_once_with('user/repo')

def test_collect_pull_requests_no_token():
    """Test that PR collection is skipped if no token is provided."""
    connector = GitConnector(repo_path='/fake/path', repo_url='https://github.com/user/repo.git')

    prs = connector.collect_pull_requests()

    assert len(prs) == 0

def test_collect_pull_requests_github_error(mock_github_client):
    """Test handling of errors from the GitHub API."""
    mock_github_client.get_repo.side_effect = GithubException(status=404, data={}, headers=None)

    connector = GitConnector(
        repo_path='/fake/path',
        repo_url='https://github.com/user/repo.git',
        github_token='fake_token'
    )

    prs = connector.collect_pull_requests()

    assert len(prs) == 0
