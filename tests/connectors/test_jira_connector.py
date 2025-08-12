import pytest
from unittest.mock import MagicMock, patch
from jira.exceptions import JIRAError
from sma_collector.connectors.jira_connector import JiraCollector

# Mock settings
@pytest.fixture(autouse=True)
def mock_settings(mocker):
    mocker.patch('sma_collector.connectors.jira_connector.settings.JIRA_SERVER', 'https://test.jira.com')
    mocker.patch('sma_collector.connectors.jira_connector.settings.JIRA_USERNAME', 'user')
    mocker.patch('sma_collector.connectors.jira_connector.settings.JIRA_API_TOKEN', 'token')
    mocker.patch('sma_collector.connectors.jira_connector.settings.JIRA_PROJECT_KEY', 'PROJ')

# Mock JIRA object
@pytest.fixture
def mock_jira_client(mocker):
    return mocker.patch('sma_collector.connectors.jira_connector.JIRA')

def test_jira_collector_initialization_success(mock_jira_client):
    """
    Test that JiraCollector initializes successfully with valid credentials.
    """
    mock_jira_instance = mock_jira_client.return_value
    collector = JiraCollector()
    mock_jira_client.assert_called_once_with(
        server='https://test.jira.com',
        basic_auth=('user', 'token')
    )
    assert collector.jira == mock_jira_instance

def test_jira_collector_initialization_failure(mock_jira_client):
    """
    Test that JiraCollector raises an exception if connection fails.
    """
    mock_jira_client.side_effect = JIRAError("Connection failed")
    with pytest.raises(JIRAError):
        JiraCollector()

def test_collect_jira_issues_success(mock_jira_client):
    """
    Test that JiraCollector successfully collects issues.
    """
    mock_jira_instance = mock_jira_client.return_value

    # Create mock issues
    mock_issue1 = MagicMock()
    mock_issue1.key = 'PROJ-1'
    mock_issue1.fields.summary = 'Test issue 1'
    mock_issue1.fields.description = 'Description for issue 1'
    mock_issue1.fields.status.name = 'Open'
    mock_issue1.fields.issuetype.name = 'Bug'
    mock_issue1.fields.reporter.displayName = 'Test User'
    mock_issue1.fields.assignee = None # Test case with no assignee
    mock_issue1.fields.created = '2023-01-01T10:00:00.000Z'
    mock_issue1.fields.updated = '2023-01-02T10:00:00.000Z'
    mock_issue1.fields.resolutiondate = None

    mock_issue2 = MagicMock()
    mock_issue2.key = 'PROJ-2'
    mock_issue2.fields.summary = 'Test issue 2'
    mock_issue2.fields.description = 'Description for issue 2'
    mock_issue2.fields.status.name = 'Closed'
    mock_issue2.fields.issuetype.name = 'Story'
    mock_issue2.fields.reporter.displayName = 'Test User'
    mock_issue2.fields.assignee.displayName = 'Another User'
    mock_issue2.fields.created = '2023-01-03T10:00:00.000Z'
    mock_issue2.fields.updated = '2023-01-04T10:00:00.000Z'
    mock_issue2.fields.resolutiondate = '2023-01-04T10:00:00.000Z'

    # Configure the mock to return issues in pages
    mock_jira_instance.search_issues.side_effect = [
        [mock_issue1, mock_issue2],
        []  # Second call returns an empty list to stop the loop
    ]

    collector = JiraCollector()
    issues = collector.collect()

    assert len(issues) == 2
    assert issues[0]['key'] == 'PROJ-1'
    assert issues[0]['assignee'] == 'N/A'
    assert issues[1]['key'] == 'PROJ-2'
    assert issues[1]['assignee'] == 'Another User'

    # Verify search_issues was called correctly
    jql = 'project = PROJ ORDER BY created DESC'
    mock_jira_instance.search_issues.assert_any_call(jql, startAt=0, maxResults=100)
    mock_jira_instance.search_issues.assert_any_call(jql, startAt=100, maxResults=100)

def test_collect_jira_issues_api_error(mock_jira_client):
    """
    Test that collection handles JIRAError during issue search.
    """
    mock_jira_instance = mock_jira_client.return_value
    mock_jira_instance.search_issues.side_effect = JIRAError("API limit reached")

    collector = JiraCollector()
    issues = collector.collect()

    assert len(issues) == 0
