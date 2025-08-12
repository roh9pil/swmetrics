import logging
from sma_collector.etl.git_collector import GitCollector
from sma_collector.etl.jira_collector import JiraCollector
from sma_collector.storage.db import Database
from sma_collector.models.models import Commit, Issue

logger = logging.getLogger(__name__)

def run_pipeline():
    """
    전체 ETL(Extract, Transform, Load) 파이프라인을 조율하고 실행합니다.
    """
    logger.info("ETL 파이프라인을 시작합니다.")
    db = Database()
    db.init_db()
    logger.info("데이터베이스가 초기화되었습니다.")

    # 1. 데이터 추출 (Extract)
    git_collector = GitCollector()
    raw_commits = git_collector.collect()
    logger.info(f"Git에서 {len(raw_commits)}개의 커밋을 수집했습니다.")

    jira_collector = JiraCollector()
    raw_issues = jira_collector.collect()
    logger.info(f"Jira에서 {len(raw_issues)}개의 이슈를 수집했습니다.")

    # 2. 데이터 변환 (Transform)
    commits = [Commit(**commit_data) for commit_data in raw_commits]
    issues = [Issue(**issue_data) for issue_data in raw_issues]

    # 3. 데이터 적재 (Load)
    with db.get_session() as session:
        try:
            # 중복을 피하기 위해 기존 데이터 삭제 (간단한 구현)
            session.query(Commit).delete()
            session.query(Issue).delete()
            
            session.bulk_save_objects(commits)
            logger.info(f"{len(commits)}개의 커밋 데이터를 데이터베이스에 저장했습니다.")
            
            session.bulk_save_objects(issues)
            logger.info(f"{len(issues)}개의 이슈 데이터를 데이터베이스에 저장했습니다.")
            
            session.commit()
            logger.info("모든 데이터가 성공적으로 커밋되었습니다.")
        except Exception as e:
            logger.error(f"데이터 저장 중 오류 발생: {e}")
            session.rollback()
            raise

