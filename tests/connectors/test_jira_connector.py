import pytest
from unittest.mock import MagicMock, patch
from jira.exceptions import JIRAError
from sma_collector.connectors.jira_connector import JiraCollector
from sma_collector.config import Settings

@pytest.fixture
def mock_settings():
    """Fixture for mock settings for Jira."""
    return Settings(
        JIRA_SERVER='https://test.jira.com',
        JIRA_USERNAME='user',
        JIRA_API_TOKEN='token',
        JIRA_PROJECT_KEY='PROJ'
    )

@patch('sma_collector.connectors.jira_connector.JIRA')
def test_jira_collector_initialization_success(mock_jira_client, mock_settings):
    """
    Test that JiraCollector initializes successfully with valid credentials.
    """
    mock_jira_instance = mock_jira_client.return_value
    collector = JiraCollector(mock_settings)
    mock_jira_client.assert_called_once_with(
        server='https://test.jira.com',
        basic_auth=('user', 'token')
    )
    assert collector.jira == mock_jira_instance

@patch('sma_collector.connectors.jira_connector.JIRA')
def test_jira_collector_initialization_failure(mock_jira_client, mock_settings):
    """
    Test that JiraCollector raises an exception if connection fails.
    """
    mock_jira_client.side_effect = JIRAError("Connection failed")
    with pytest.raises(JIRAError):
        JiraCollector(mock_settings)

@patch('sma_collector.connectors.jira_connector.JIRA')
def test_collect_jira_issues_success(mock_jira_client, mock_settings):
    """
    Test that JiraCollector successfully collects issues.
    """
    mock_jira_instance = mock_jira_client.return_value

    mock_issue1 = MagicMock()
    mock_issue1.key = 'PROJ-1'
    mock_issue1.fields.summary = 'Test issue 1'
    # ... (rest of the mock issue setup is the same)

    mock_jira_instance.search_issues.side_effect = [[mock_issue1], []]

    collector = JiraCollector(mock_settings)
    issues = collector.collect()

    assert len(issues) == 1
    assert issues[0]['key'] == 'PROJ-1'

@patch('sma_collector.connectors.jira_connector.JIRA')
def test_collect_jira_issues_api_error(mock_jira_client, mock_settings):
    """
    Test that collection handles JIRAError during issue search.
    """
    mock_jira_instance = mock_jira_client.return_value
    mock_jira_instance.search_issues.side_effect = JIRAError("API limit reached")

    collector = JiraCollector(mock_settings)
    issues = collector.collect()

    assert len(issues) == 0