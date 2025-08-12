import logging
from sma_collector.connectors.git_connector import GitConnector
from sma_collector.connectors.jira_connector import JiraCollector
from sma_collector.connectors.bitbucket_connector import BitbucketConnector
from sma_collector.connectors.swarm_connector import SwarmConnector
from sma_collector.database.models import Commit, Issue, CodeReview, bulk_upsert, get_db_session
from sma_collector.config import settings

logger = logging.getLogger(__name__)

def run_pipeline():
    """
    전체 ETL(Extract, Transform, Load) 파이프라인을 조율하고 실행합니다.
    """
    logger.info("ETL 파이프라인을 시작합니다.")

    session = get_db_session()
    logger.info("데이터베이스 세션이 생성되었습니다.")

    try:
        # 1. 데이터 추출 (Extract)
        git_collector = GitConnector(repo_path=settings.GIT_REPO_PATH)
        raw_commits = git_collector.collect()
        logger.info(f"Git에서 {len(raw_commits)}개의 커밋을 수집했습니다.")
        bulk_upsert(session, Commit, raw_commits)
        logger.info(f"{len(raw_commits)}개의 커밋 데이터를 데이터베이스에 저장(upsert)했습니다.")

        jira_collector = JiraCollector()
        raw_issues = jira_collector.collect()
        logger.info(f"Jira에서 {len(raw_issues)}개의 이슈를 수집했습니다.")

        # Transform and Load Jira issues
        transformed_issues = []
        for issue_data in raw_issues:
            transformed_issues.append({
                "id": issue_data["key"], "issue_key": issue_data["key"], "type": issue_data["issue_type"],
                "status": issue_data["status"], "title": issue_data["summary"], "created_date": issue_data["created"],
                "resolved_date": issue_data["resolved"],
            })
        bulk_upsert(session, Issue, transformed_issues)
        logger.info(f"{len(transformed_issues)}개의 이슈 데이터를 데이터베이스에 저장(upsert)했습니다.")

        # Bitbucket 데이터 수집
        bitbucket_collector = BitbucketConnector()
        # Note: In a real application, you would loop through projects and repositories.
        # For this example, we assume a single target.
        # You would need to add configuration for these.
        # For now, this will likely fail unless the user has a project and repo with these exact keys.
        # This is a simplification for now.
        raw_bitbucket_reviews = bitbucket_collector.collect_pull_requests(project_key="PROJ", repository_slug="repo")
        logger.info(f"Bitbucket에서 {len(raw_bitbucket_reviews)}개의 풀 리퀘스트를 수집했습니다.")
        bulk_upsert(session, CodeReview, raw_bitbucket_reviews)
        logger.info(f"{len(raw_bitbucket_reviews)}개의 Bitbucket 리뷰 데이터를 데이터베이스에 저장(upsert)했습니다.")

        # Swarm 데이터 수집
        swarm_collector = SwarmConnector()
        raw_swarm_reviews = swarm_collector.collect()
        logger.info(f"Swarm에서 {len(raw_swarm_reviews)}개의 리뷰를 수집했습니다.")
        bulk_upsert(session, CodeReview, raw_swarm_reviews)
        logger.info(f"{len(raw_swarm_reviews)}개의 Swarm 리뷰 데이터를 데이터베이스에 저장(upsert)했습니다.")

        session.commit()
        logger.info("모든 데이터가 성공적으로 커밋되었습니다.")
    except Exception as e:
        logger.error(f"데이터 저장 중 오류 발생: {e}")
        session.rollback()
        raise
    finally:
        session.close()

