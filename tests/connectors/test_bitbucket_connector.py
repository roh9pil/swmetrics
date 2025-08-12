import unittest
from unittest.mock import patch, MagicMock
from sma_collector.connectors.bitbucket_connector import BitbucketConnector

class TestBitbucketConnector(unittest.TestCase):

    @patch('sma_collector.connectors.bitbucket_connector.Bitbucket')
    def test_collect_pull_requests_success(self, mock_bitbucket):
        # Mock the Bitbucket API response
        mock_api = MagicMock()
        mock_bitbucket.return_value = mock_api
        mock_api.get_pull_requests.return_value = [
            {
                "id": 1,
                "title": "Test PR 1",
                "author": {"user": {"displayName": "User1"}},
                "createdDate": "2023-01-01T12:00:00Z",
                "mergedDate": "2023-01-02T12:00:00Z",
                "state": "MERGED"
            },
            {
                "id": 2,
                "title": "Test PR 2",
                "author": {"user": {"displayName": "User2"}},
                "createdDate": "2023-01-03T12:00:00Z",
                "mergedDate": None,
                "state": "OPEN"
            }
        ]

        # Initialize the connector and collect data
        connector = BitbucketConnector()
        reviews = connector.collect_pull_requests(project_key="PROJ", repository_slug="repo")

        # Assertions
        self.assertEqual(len(reviews), 2)
        self.assertEqual(reviews[0]['pr_number'], 1)
        self.assertEqual(reviews[0]['author'], 'User1')
        self.assertEqual(reviews[1]['state'], 'OPEN')
        mock_api.get_pull_requests.assert_called_once_with("PROJ", "repo", state="ALL")

    @patch('sma_collector.connectors.bitbucket_connector.Bitbucket')
    def test_collect_pull_requests_api_error(self, mock_bitbucket):
        # Mock the Bitbucket API to raise an exception
        mock_api = MagicMock()
        mock_bitbucket.return_value = mock_api
        mock_api.get_pull_requests.side_effect = Exception("API Error")

        # Initialize the connector and collect data
        connector = BitbucketConnector()
        reviews = connector.collect_pull_requests(project_key="PROJ", repository_slug="repo")

        # Assertions
        self.assertEqual(len(reviews), 0)

if __name__ == '__main__':
    unittest.main()
