import logging
from typing import List, Dict, Any
from jira import JIRA, JIRAError
from sma_collector.config import settings
from .collector import BaseCollector

logger = logging.getLogger(__name__)

class JiraCollector(BaseCollector):
    """
    Jira 서버에서 이슈 데이터를 수집하는 클래스.
    """
    def __init__(self):
        try:
            self.jira = JIRA(
                server=settings.JIRA_SERVER,
                basic_auth=(settings.JIRA_USERNAME, settings.JIRA_API_TOKEN)
            )
            logger.info(f"Jira 서버 '{settings.JIRA_SERVER}'에 연결되었습니다.")
        except JIRAError as e:
            logger.error(f"Jira 연결 실패: {e.text}")
            raise

    def collect(self) -> List[Dict[str, Any]]:
        all_issues_data = []
        jql = f'project = {settings.JIRA_PROJECT_KEY} ORDER BY created DESC'
        block_size = 100
        block_num = 0
        
        while True:
            try:
                start_at = block_num * block_size
                issues = self.jira.search_issues(jql, startAt=start_at, maxResults=block_size)
                if not issues:
                    break
                
                for issue in issues:
                    fields = issue.fields
                    issue_data = {
                        "key": issue.key,
                        "summary": fields.summary,
                        "description": fields.description or "",
                        "status": fields.status.name,
                        "issue_type": fields.issuetype.name,
                        "reporter": fields.reporter.displayName if fields.reporter else "N/A",
                        "assignee": fields.assignee.displayName if fields.assignee else "N/A",
                        "created": fields.created,
                        "updated": fields.updated,
                        "resolved": fields.resolutiondate,
                    }
                    all_issues_data.append(issue_data)
                block_num += 1
            except JIRAError as e:
                logger.error(f"Jira 이슈 검색 중 오류 발생: {e.text}")
                break
        return all_issues_data

