import logging
from datetime import datetime
from..database.models import (
    get_db_session, bulk_upsert, Commit, Issue, Build, BuildCommit, 
    Deployment, Incident, VtsRun, OspMetric,
    TeamSurvey, CodeReview, CodeQualityMetric
)
from..connectors.git_connector import GitConnector
from..connectors.jira_connector import JiraConnector
from..connectors.jenkins_connector import JenkinsConnector
from..connectors.android_connector import AndroidConnector
from..connectors.survey_connector import SurveyConnector
from..connectors.sonarqube_connector import SonarQubeConnector
from..config import settings

def run_pipeline():
    logging.info("Starting ETL pipeline (Phase 3)...")
    session = get_db_session()

    try:
        # --- 1. EXTRACT ---
        git = GitConnector(settings.GIT_REPO_URL, "/app/repo", settings.GITHUB_TOKEN)
        commits_data = git.collect_commits()
        reviews_data = git.collect_pull_requests()

        jira = JiraConnector(settings.JIRA_HOST, settings.JIRA_USER, settings.JIRA_TOKEN)
        issues_data = jira.collect_issues(settings.JIRA_PROJECT_KEY)

        jenkins = JenkinsConnector(settings.JENKINS_HOST, settings.JENKINS_USER, settings.JENKINS_TOKEN)
        builds_data, build_commits_map = jenkins.collect_builds(settings.JENKINS_JOB_NAME)

        android = AndroidConnector(settings.VTS_RESULTS_PATH, settings.PROFILING_DATA_PATH)
        vts_runs_data = android.collect_vts_results()
        osp_metrics_data = android.collect_perfetto_traces() + android.collect_battery_historian_logs()

        survey = SurveyConnector(settings.SURVEY_DATA_PATH)
        survey_data = survey.collect_satisfaction_scores()

        sonarqube = SonarQubeConnector(settings.SONARQUBE_HOST, settings.SONARQUBE_TOKEN)
        quality_metrics_data = sonarqube.collect_quality_metrics(settings.SONARQUBE_PROJECT_KEY)

        # --- 2. LOAD (raw & semi-transformed data) ---
        bulk_upsert(session, Commit, commits_data)
        bulk_upsert(session, Issue, issues_data)
        bulk_upsert(session, Build, builds_data)
        bulk_upsert(session, CodeReview, reviews_data)
        bulk_upsert(session, VtsRun, vts_runs_data)
        bulk_upsert(session, OspMetric, osp_metrics_data)
        bulk_upsert(session, TeamSurvey, survey_data)
        bulk_upsert(session, CodeQualityMetric, quality_metrics_data)

        all_build_commits = []
        for build_id, commit_shas in build_commits_map.items():
            for sha in commit_shas:
                all_build_commits.append({"build_id": build_id, "commit_sha": sha})
        bulk_upsert(session, BuildCommit, all_build_commits)

        # --- 3. TRANSFORM & LOAD (derived data) ---
        deployments = []
        for build in builds_data:
            if settings.DEPLOYMENT_JOB_NAME_PATTERN in build['job_name'] and build['status'] == 'SUCCESS':
                commits_in_build = build_commits_map.get(build['id'], [])
                rep_commit = commits_in_build[0] if commits_in_build else None
                deployments.append({
                    "id": build['id'],
                    "commit_sha": rep_commit,
                    "start_time": build['start_time'],
                    "finish_time": build['finish_time'],
                })
        bulk_upsert(session, Deployment, deployments)
        logging.info(f"Transformed and loaded {len(deployments)} deployments.")

        incidents = []
        for issue in issues_data:
            if issue['type'] in ['Bug']:
                related_deployment_id = None
                latest_deployment_time = None
                for dep in deployments:
                    if dep['finish_time'] < issue['created_date']:
                        if latest_deployment_time is None or dep['finish_time'] > latest_deployment_time:
                            latest_deployment_time = dep['finish_time']
                            related_deployment_id = dep['id']
                
                incidents.append({
                    "id": issue['id'],
                    "deployment_id": related_deployment_id,
                    "created_date": issue['created_date'],
                    "resolved_date": issue['resolved_date'],
                })
        bulk_upsert(session, Incident, incidents)
        logging.info(f"Transformed and loaded {len(incidents)} incidents.")

    finally:
        session.close()
    logging.info("ETL pipeline (Phase 3) finished successfully.")

