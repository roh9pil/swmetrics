# sma_collector/connectors/sonarqube_connector.py
import logging
from datetime import date
from sonarqube import SonarQubeClient

class SonarQubeConnector:
    def __init__(self, host: str | None, token: str | None):
        self.client = None
        if host and token:
            self.client = SonarQubeClient(sonarqube_url=host, token=token)

    def collect_quality_metrics(self, project_key: str | None) -> list[dict]:
        metrics =
        if not (self.client and project_key):
            logging.warning("SonarQube host/token/project_key not provided. Skipping quality metrics collection.")
            return metrics
        try:
            metric_keys = "sqale_debt_ratio,complexity,violations"
            component_measures = self.client.measures.get_component_measures(
                component=project_key,
                metricKeys=metric_keys
            )
            analysis_date = date.today()
            for measure in component_measures['component']['measures']:
                metric_name = ""
                if measure['metric'] == 'sqale_debt_ratio': metric_name = 'TECHNICAL_DEBT_RATIO'
                elif measure['metric'] == 'complexity': metric_name = 'CYCLOMATIC_COMPLEXITY'
                elif measure['metric'] == 'violations': metric_name = 'MISRA_VIOLATIONS'
                
                if metric_name:
                    metrics.append({
                        "analysis_date": analysis_date,
                        "project_key": project_key,
                        "metric_name": metric_name,
                        "metric_value": float(measure['value'])
                    })
            logging.info(f"Collected {len(metrics)} quality metrics from SonarQube for project {project_key}.")
        except Exception as e:
            logging.error(f"Failed to collect SonarQube metrics: {e}")
        return metrics
