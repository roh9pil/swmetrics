import logging
from sma_collector.etl.pipeline import run_pipeline
from sma_collector.config import settings

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """
    데이터 수집 CLI의 메인 진입점입니다.
    설정을 로드하고 ETL 파이프라인을 실행합니다.
    """
    logger.info("=================================================")
    logger.info("  Software Metrics Analyzer (SMA) Collector 시작")
    logger.info("=================================================")
    
    logger.info(f"Jira 서버: {settings.JIRA_SERVER}")
    logger.info(f"분석할 Git 레포지토리: {settings.GIT_REPO_PATH}")
    logger.info(f"데이터베이스 경로: {settings.DATABASE_URL}")
    
    try:
        run_pipeline()
        logger.info("ETL 파이프라인이 성공적으로 완료되었습니다.")
    except Exception as e:
        logger.error(f"파이프라인 실행 중 오류 발생: {e}", exc_info=True)
    finally:
        logger.info("SMA Collector 실행 종료.")

if __name__ == "__main__":
    main()


