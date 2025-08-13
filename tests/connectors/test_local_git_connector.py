import pytest
from unittest.mock import MagicMock, patch
from sma_collector.connectors.local_git_connector import LocalGitConnector
from sma_collector.config import Settings

@pytest.fixture
def mock_settings():
    """Fixture for mock settings."""
    return Settings(
        GIT_REPO_PATH="/fake/repo",
        GIT_REPO_URL="https://github.com/fake/repo.git"
    )

@patch('sma_collector.connectors.local_git_connector.Repo')
def test_local_git_connector_collect(mock_repo, mock_settings):
    """Test the collect method of LocalGitConnector."""
    # Arrange
    mock_commit = MagicMock()
    mock_commit.hexsha = "12345"
    mock_commit.author.name = "Test Author"
    mock_commit.author.email = "test@example.com"
    mock_commit.message = "Test commit"
    mock_commit.authored_datetime = "2025-01-01T12:00:00Z"

    mock_repo_instance = MagicMock()
    mock_repo_instance.iter_commits.return_value = [mock_commit]
    mock_repo.return_value = mock_repo_instance

    connector = LocalGitConnector(mock_settings)
    connector._repo = mock_repo_instance # Inject the mocked repo object

    # Act
    commits = connector.collect()

    # Assert
    assert len(commits) == 1
    assert commits[0]['sha'] == "12345"
    assert commits[0]['author_name'] == "Test Author"
    mock_repo_instance.iter_commits.assert_called_once_with('HEAD', max_count=1000)
