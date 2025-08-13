import pytest
from unittest.mock import MagicMock, patch
# from sma_collector.connectors.github_connector import GitHubConnector
from sma_collector.config import Settings

@pytest.fixture
def mock_settings():
    """Fixture for mock settings with GitHub configuration."""
    return Settings(
        GIT_REPO_URL="https://github.com/fake/repo.git",
        GITHUB_TOKEN="fake_token"
    )

@patch('sma_collector.connectors.github_connector.Github')
def test_github_connector_collect(mock_github, mock_settings):
    """Test the collect method of GitHubConnector."""
    # Arrange
    mock_pr = MagicMock()
    mock_pr.number = 1
    mock_pr.title = "Test PR"
    mock_pr.user.login = "testuser"
    mock_pr.created_at = "2025-01-01T12:00:00Z"
    mock_pr.merged_at = "2025-01-01T13:00:00Z"
    mock_pr.state = "closed"

    mock_repo = MagicMock()
    mock_repo.id = 123
    mock_repo.get_pulls.return_value = [mock_pr]

    mock_github_instance = MagicMock()
    mock_github_instance.get_repo.return_value = mock_repo
    mock_github.return_value = mock_github_instance

    connector = GitHubConnector(mock_settings)

    # Act
    pull_requests = connector.collect()

    # Assert
    assert len(pull_requests) == 1
    assert pull_requests[0]['pr_number'] == 1
    assert pull_requests[0]['title'] == "Test PR"
    assert pull_requests[0]['author'] == "testuser"
    mock_github_instance.get_repo.assert_called_once_with("fake/repo")
    mock_repo.get_pulls.assert_called_once_with(state='all', sort='created', direction='desc')
