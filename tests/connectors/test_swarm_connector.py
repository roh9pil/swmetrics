import unittest
from unittest.mock import patch, MagicMock
from sma_collector.connectors.swarm_connector import SwarmConnector
import requests

class TestSwarmConnector(unittest.TestCase):

    @patch('sma_collector.connectors.swarm_connector.requests.Session')
    def test_collect_reviews_success(self, mock_session):
        # Mock the Swarm API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "reviews": [
                {
                    "id": 101,
                    "projectName": "MyProject",
                    "description": "Review 101",
                    "author": "SwarmUser1",
                    "created": "2023-02-01T10:00:00Z",
                    "state": "needsReview"
                },
                {
                    "id": 102,
                    "projectName": "MyProject",
                    "description": "Review 102",
                    "author": "SwarmUser2",
                    "created": "2023-02-02T11:00:00Z",
                    "state": "approved"
                }
            ]
        }
        mock_response.raise_for_status.return_value = None

        mock_api = MagicMock()
        mock_api.get.return_value = mock_response
        mock_session.return_value = mock_api

        # Initialize the connector and collect data
        connector = SwarmConnector()
        reviews = connector.collect_reviews()

        # Assertions
        self.assertEqual(len(reviews), 2)
        self.assertEqual(reviews[0]['pr_number'], 101)
        self.assertEqual(reviews[0]['author'], 'SwarmUser1')
        self.assertEqual(reviews[1]['state'], 'approved')

    @patch('sma_collector.connectors.swarm_connector.requests.Session')
    def test_collect_reviews_api_error(self, mock_session):
        # Mock the Swarm API to raise an exception during review collection
        # but succeed during initialization.
        mock_api = MagicMock()

        # Successful connection test response
        mock_init_response = MagicMock()
        mock_init_response.raise_for_status.return_value = None

        # Set up side_effect to handle multiple calls to get()
        mock_api.get.side_effect = [
            mock_init_response,  # First call in __init__
            requests.exceptions.RequestException("API Error")  # Second call in collect_reviews
        ]
        mock_session.return_value = mock_api

        # Initialize the connector
        connector = SwarmConnector()

        # Collect data, which should now trigger the exception
        reviews = connector.collect_reviews()

        # Assertions
        self.assertEqual(len(reviews), 0)

if __name__ == '__main__':
    unittest.main()
