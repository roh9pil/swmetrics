import os
import pika
import json
import time
import logging
from sma_collector.config import settings
from sma_collector.database.models import get_db_session
from sma_collector.registry import register_connector, register_processor, CONNECTOR_REGISTRY, PROCESSOR_REGISTRY
from sma_collector.connectors.local_git_connector import LocalGitConnector
from sma_collector.connectors.github_connector import GitHubConnector
from sma_collector.connectors.jira_connector import JiraCollector
from sma_collector.processors import process_git_data, process_github_data, process_jira_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_registry():
    """Registers all the available connectors and processors."""
    register_connector('git', LocalGitConnector)
    register_connector('github', GitHubConnector)
    register_connector('jira', JiraCollector)

    register_processor('git', process_git_data)
    register_processor('github', process_github_data)
    register_processor('jira', process_jira_data)

def callback(ch, method, properties, body):
    job = json.loads(body)
    logger.info(f" [x] Received job: {job}")

    source = job.get('source')
    session = get_db_session()

    try:
        connector_class = CONNECTOR_REGISTRY.get(source)
        processor_function = PROCESSOR_REGISTRY.get(source)

        if connector_class and processor_function:
            logger.info(f"Starting {source} collection...")
            connector = connector_class(settings)
            data = connector.collect()
            processor_function(session, data)
            logger.info(f"{source} collection finished.")
        else:
            logger.warning(f"Unknown source: {source}")

    except Exception as e:
        logger.error(f"An error occurred processing job {job}: {e}", exc_info=True)
    finally:
        session.close()
        ch.basic_ack(delivery_tag=method.delivery_tag)
        logger.info(f"Finished processing job: {job}")


def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.RABBITMQ_HOST, heartbeat=600, blocked_connection_timeout=300))
    channel = connection.channel()

    channel.queue_declare(queue='collection_jobs', durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='collection_jobs', on_message_callback=callback)

    logger.info(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    setup_registry()
    time.sleep(10)
    main()
