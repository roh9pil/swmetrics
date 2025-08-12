import logging
from typing import List, Dict, Any
from atlassian import Bitbucket
from sma_collector.config import settings
from .collector import BaseCollector

logger = logging.getLogger(__name__)

class BitbucketConnector(BaseCollector):
    """
    Bitbucket 서버에서 커밋 및 풀 리퀘스트 데이터를 수집하는 클래스.
    """
    def __init__(self):
        try:
            self.bitbucket = Bitbucket(
                url=settings.BITBUCKET_SERVER,
                username=settings.BITBUCKET_USERNAME,
                password=settings.BITBUCKET_API_TOKEN
            )
            logger.info(f"Bitbucket 서버 '{settings.BITBUCKET_SERVER}'에 연결되었습니다.")
        except Exception as e:
            logger.error(f"Bitbucket 연결 실패: {e}")
            raise

    def collect(self) -> List[Dict[str, Any]]:
        # For now, we will focus on collecting pull requests, as they are equivalent to code reviews.
        # We can extend this to collect commits later if needed.
        return self.collect_pull_requests()

    def collect_pull_requests(self, project_key: str, repository_slug: str) -> List[Dict[str, Any]]:
        """
        지정된 프로젝트와 레포지토리에서 풀 리퀘스트 목록을 수집합니다.
        """
        pull_requests_data = []
        try:
            prs = self.bitbucket.get_pull_requests(project_key, repository_slug, state="ALL")
            for pr in prs:
                pull_requests_data.append({
                    "id": f"{project_key}-{repository_slug}-{pr['id']}",
                    "repo_name": f"{project_key}/{repository_slug}",
                    "pr_number": pr['id'],
                    "title": pr['title'],
                    "author": pr['author']['user']['displayName'],
                    "created_date": pr['createdDate'],
                    "merged_date": pr.get('mergedDate'),
                    "state": pr['state'],
                })
            logger.info(f"Collected {len(pull_requests_data)} pull requests from Bitbucket.")
        except Exception as e:
            logger.error(f"Bitbucket 풀 리퀘스트 수집 중 오류 발생: {e}")

        return pull_requests_data
