import logging
from sqlalchemy.orm import Session
from sma_collector.database.models import Commit, CodeReview, Issue, bulk_upsert

logger = logging.getLogger(__name__)

def process_git_data(session: Session, data):
    """Processes and stores commit data."""
    if data:
        bulk_upsert(session, Commit, data)
        logger.info(f"Upserted {len(data)} commits.")

def process_github_data(session: Session, data):
    """Processes and stores pull request data."""
    if data:
        pr_data = [
            {
                "id": pr["id"],
                "repo_name": pr["repo_name"],
                "pr_number": pr["pr_number"],
                "title": pr["title"],
                "author": pr["author"],
                "created_date": pr["created_date"],
                "merged_date": pr["merged_date"],
            } for pr in data
        ]
        bulk_upsert(session, CodeReview, pr_data)
        logger.info(f"Upserted {len(pr_data)} pull requests as code reviews.")

def process_jira_data(session: Session, data):
    """Processes and stores issue data."""
    if data:
        issue_data = [
            {
                "id": issue["key"],
                "issue_key": issue["key"],
                "type": issue["issue_type"],
                "status": issue["status"],
                "title": issue["summary"],
                "created_date": issue["created"],
                "resolved_date": issue["resolved"],
            } for issue in data
        ]
        bulk_upsert(session, Issue, issue_data)
        logger.info(f"Upserted {len(issue_data)} issues.")
