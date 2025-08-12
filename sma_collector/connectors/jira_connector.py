# sma_collector/connectors/jira_connector.py
import logging
from jira import JIRA
from datetime import datetime

class JiraConnector:
    def __init__(self, host: str, user: str, token: str):
        self.client = JIRA(server=host, basic_auth=(user, token))

    def collect_issues(self, project_key: str, max_results=100) -> list[dict]:
        jql = f"project = {project_key} ORDER BY created DESC"
        issues_raw = self.client.search_issues(jql, maxResults=max_results)
        
        issues =
        for issue in issues_raw:
            resolved_date_str = issue.fields.resolutiondate
            resolved_date = datetime.fromisoformat(resolved_date_str.replace('Z', '+00:00')) if resolved_date_str else None
            created_date_str = issue.fields.created
            created_date = datetime.fromisoformat(created_date_str.replace('Z', '+00:00')) if created_date_str else None
            
            lead_time = None
            if resolved_date and created_date:
                lead_time = (resolved_date - created_date).total_seconds() / 60

            sli = None
            for label in issue.fields.labels:
                if label.lower().startswith("sli-"):
                    try:
                        sli = int(label.split('-')[1])
                        break
                    except (ValueError, IndexError):
                        pass

            issues.append({
                "id": issue.id,
                "issue_key": issue.key,
                "type": self._normalize_issue_type(issue.fields.issuetype.name),
                "status": self._normalize_issue_status(issue.fields.status.name),
                "title": issue.fields.summary,
                "created_date": created_date,
                "resolved_date": resolved_date,
                "lead_time_minutes": int(lead_time) if lead_time is not None else None,
                "sli": sli,
            })
        logging.info(f"Collected {len(issues)} issues from Jira.")
        return issues

    def _normalize_issue_type(self, jira_type: str) -> str:
        lower_type = jira_type.lower()
        if "bug" in lower_type: return "BUG"
        if "incident" in lower_type: return "INCIDENT"
        return "REQUIREMENT"

    def _normalize_issue_status(self, jira_status: str) -> str:
        lower_status = jira_status.lower()
        if lower_status in ["done", "closed", "resolved", "complete"]: return "DONE"
        if lower_status in ["in progress", "in review", "in qa"]: return "IN_PROGRESS"
        return "TODO"

