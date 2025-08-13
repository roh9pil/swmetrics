import pytest
from unittest.mock import MagicMock, patch, call
import json
import pika

from sma_collector import main as producer_main
from sma_collector import collector_worker

@patch('sma_collector.main.pika.BlockingConnection')
def test_main_dispatches_jobs(mock_blocking_connection):
    """
    Test that the main dispatcher sends the correct jobs to the queue.
    """
    # Setup mock objects
    mock_channel = MagicMock()
    mock_connection = MagicMock()
    mock_connection.channel.return_value = mock_channel
    mock_blocking_connection.return_value = mock_connection

    # Run the producer main function
    producer_main.main()

    # Assert that a connection was made
    mock_blocking_connection.assert_called_once()
    mock_connection.channel.assert_called_once()
    mock_channel.queue_declare.assert_called_once_with(queue='collection_jobs')

    # Assert that both jobs were published
    assert mock_channel.basic_publish.call_count == 2

    # Check the calls to basic_publish
    expected_calls = [
        call(
            exchange='',
            routing_key='collection_jobs',
            body=json.dumps({'source': 'git'}),
            properties=pika.BasicProperties(delivery_mode=2)
        ),
        call(
            exchange='',
            routing_key='collection_jobs',
            body=json.dumps({'source': 'jira'}),
            properties=pika.BasicProperties(delivery_mode=2)
        )
    ]
    mock_channel.basic_publish.assert_has_calls(expected_calls, any_order=True)


@patch('sma_collector.collector_worker.JiraCollector')
@patch('sma_collector.collector_worker.GitConnector')
@patch('sma_collector.collector_worker.settings')
def test_worker_callback(mock_settings, mock_git_connector, mock_jira_collector):
    """
    Test that the worker callback correctly processes jobs.
    """
    # --- Test Git Job ---
    # Setup mock objects
    mock_channel = MagicMock()
    mock_method = MagicMock()
    mock_method.delivery_tag = 123
    git_job_body = json.dumps({'source': 'git'})

    # Call the callback with a git job
    collector_worker.callback(mock_channel, mock_method, None, git_job_body)

    # Assert GitConnector was called
    mock_git_connector.assert_called_once()
    mock_git_connector.return_value.collect.assert_called_once()
    # Assert JiraConnector was NOT called
    mock_jira_collector.assert_not_called()
    # Assert message was acknowledged
    mock_channel.basic_ack.assert_called_once_with(delivery_tag=123)

    # --- Reset mocks for next test ---
    mock_git_connector.reset_mock()
    mock_jira_collector.reset_mock()
    mock_channel.reset_mock()

    # --- Test Jira Job ---
    jira_job_body = json.dumps({'source': 'jira'})
    mock_method.delivery_tag = 456

    # Call the callback with a jira job
    collector_worker.callback(mock_channel, mock_method, None, jira_job_body)

    # Assert JiraConnector was called
    mock_jira_collector.assert_called_once()
    mock_jira_collector.return_value.collect.assert_called_once()
    # Assert GitConnector was NOT called
    mock_git_connector.assert_not_called()
    # Assert message was acknowledged
    mock_channel.basic_ack.assert_called_once_with(delivery_tag=456)
