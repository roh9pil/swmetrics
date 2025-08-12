# sma_collector/connectors/jenkins_connector.py
import logging
import jenkins
from datetime import datetime, timezone, timedelta

class JenkinsConnector:
    def __init__(self, host: str, user: str, token: str):
        self.server = jenkins.Jenkins(host, username=user, password=token)

    def collect_builds(self, job_name: str, max_builds=100) -> tuple[list[dict], dict]:
        builds = []
        build_commits_map = {}
        try:
            job_info = self.server.get_job_info(job_name, depth=1)
            build_numbers = [b['number'] for b in job_info.get('builds', [])[:max_builds]]

            for number in build_numbers:
                try:
                    build_info = self.server.get_build_info(job_name, number)
                    start_time = datetime.fromtimestamp(build_info['timestamp'] / 1000, tz=timezone.utc)
                    finish_time = start_time + timedelta(milliseconds=build_info['duration'])

                    builds.append({
                        "id": build_info['url'],
                        "job_name": job_name,
                        "number": build_info['number'],
                        "status": self._normalize_status(build_info['result']),
                        "start_time": start_time,
                        "finish_time": finish_time,
                        "duration_millis": build_info['duration'],
                    })
                    
                    commits = [change['commitId'] for change in build_info.get('changeSet', {}).get('items', []) if 'commitId' in change]
                    build_commits_map[build_info['url']] = commits
                except jenkins.JenkinsException as e:
                    logging.warning(f"Could not get build {number}: {e}")
        except jenkins.JenkinsException as e:
            logging.error(f"Failed to get job info for {job_name}: {e}")

        logging.info(f"Collected {len(builds)} builds from Jenkins.")
        return builds, build_commits_map

    def _normalize_status(self, result: str | None) -> str:
        if result == "SUCCESS": return "SUCCESS"
        if result == "FAILURE": return "FAILURE"
        return "ABORTED"
