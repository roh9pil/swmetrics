import pytest
from unittest.mock import MagicMock, patch
from sma_collector.processors import process_git_data, process_github_data, process_jira_data

@pytest.fixture
def mock_session():
    """Fixture for a mock database session."""
    return MagicMock()

@patch('sma_collector.processors.bulk_upsert')
def test_process_git_data(mock_bulk_upsert, mock_session):
    """Test the process_git_data function."""
    # Arrange
    git_data = [{"sha": "12345", "author_name": "Test Author"}]

    # Act
    process_git_data(mock_session, git_data)

    # Assert
    mock_bulk_upsert.assert_called_once()
    args, _ = mock_bulk_upsert.call_args
    assert args[0] == mock_session
    # args[1] is the Model class, which is fine
    assert args[2] == git_data

@patch('sma_collector.processors.bulk_upsert')
def test_process_github_data(mock_bulk_upsert, mock_session):
    """Test the process_github_data function."""
    # Arrange
    github_data = [{
        "id": "123-1", "repo_name": "fake/repo", "pr_number": 1,
        "title": "Test PR", "author": "testuser",
        "created_date": "2025-01-01T12:00:00Z", "merged_date": "2025-01-01T13:00:00Z"
    }]

    # Act
    process_github_data(mock_session, github_data)

    # Assert
    mock_bulk_upsert.assert_called_once()
    args, _ = mock_bulk_upsert.call_args
    assert len(args[2]) == 1
    assert args[2][0]['pr_number'] == 1

@patch('sma_collector.processors.bulk_upsert')
def test_process_jira_data(mock_bulk_upsert, mock_session):
    """Test the process_jira_data function."""
    # Arrange
    jira_data = [{
        "key": "PROJ-1", "issue_type": "Bug", "status": "Done",
        "summary": "Test issue", "created": "2025-01-01T12:00:00Z",
        "resolved": "2025-01-01T13:00:00Z"
    }]

    # Act
    process_jira_data(mock_session, jira_data)

    # Assert
    mock_bulk_upsert.assert_called_once()
    args, _ = mock_bulk_upsert.call_args
    assert len(args[2]) == 1
    assert args[2][0]['issue_key'] == "PROJ-1"
