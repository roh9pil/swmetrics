import logging
import requests
from typing import List, Dict, Any
from sma_collector.config import settings
from .collector import BaseCollector

logger = logging.getLogger(__name__)

class SwarmConnector(BaseCollector):
    """
    Swarm에서 코드 리뷰 데이터를 수집하는 클래스.
    """
    def __init__(self):
        self.swarm_url = settings.SWARM_SERVER
        self.username = settings.SWARM_USERNAME
        self.api_token = settings.SWARM_API_TOKEN
        self.session = requests.Session()
        self.session.auth = (self.username, self.api_token)

        # Test connection
        try:
            response = self.session.get(f"{self.swarm_url}/api/v9/reviews", params={"max": 1})
            response.raise_for_status()
            logger.info(f"Swarm 서버 '{self.swarm_url}'에 연결되었습니다.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Swarm 연결 실패: {e}")
            raise

    def collect(self) -> List[Dict[str, Any]]:
        return self.collect_reviews()

    def collect_reviews(self, max_reviews: int = 100) -> List[Dict[str, Any]]:
        """
        Swarm에서 코드 리뷰 목록을 수집합니다.
        """
        reviews_data = []
        try:
            response = self.session.get(
                f"{self.swarm_url}/api/v9/reviews",
                params={"max": max_reviews, "fields": "id,author,created,description,state,projectName,participants"}
            )
            response.raise_for_status()
            reviews = response.json().get("reviews", [])

            for review in reviews:
                reviews_data.append({
                    "id": f"swarm-{review['id']}",
                    "repo_name": review.get("projectName", "N/A"),
                    "pr_number": review['id'],
                    "title": review.get("description", "").split('\\n')[0],
                    "author": review.get("author", "N/A"),
                    "created_date": review.get("created"),
                    "merged_date": None,  # Swarm API does not provide a direct merged date for reviews
                    "state": review.get("state"),
                })
            logger.info(f"Collected {len(reviews_data)} reviews from Swarm.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Swarm 리뷰 수집 중 오류 발생: {e}")

        return reviews_data
