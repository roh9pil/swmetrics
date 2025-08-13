
import os
import pika
import json
import time
import logging
from sma_collector.connectors.git_connector import GitConnector
from sma_collector.connectors.jira_connector import JiraCollector
from sma_collector.config import settings
from sma_collector.database.models import Commit, CodeReview, Issue, get_db_session, bulk_upsert

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def callback(ch, method, properties, body):
    job = json.loads(body)
    logger.info(f" [x] Received job: {job}")

    source = job.get('source')
    session = get_db_session()

    try:
        if source == 'git':
            logger.info("Starting Git collection...")
            connector = GitConnector(
                repo_path=settings.GIT_REPO_PATH,
                repo_url=settings.GIT_REPO_URL,
                github_token=settings.GITHUB_TOKEN
            )
            data = connector.collect()

            if data.get('commits'):
                bulk_upsert(session, Commit, data['commits'])
                logger.info(f"Upserted {len(data['commits'])} commits.")

            if data.get('pull_requests'):
                # The model is CodeReview, so we need to map the fields
                pr_data = [
                    {
                        "id": pr["id"],
                        "repo_name": pr["repo_name"],
                        "pr_number": pr["pr_number"],
                        "title": pr["title"],
                        "author": pr["author"],
                        "created_date": pr["created_date"],
                        "merged_date": pr["merged_date"],
                        # 'state' from collector is not in 'CodeReview' model
                    } for pr in data['pull_requests']
                ]
                bulk_upsert(session, CodeReview, pr_data)
                logger.info(f"Upserted {len(pr_data)} pull requests as code reviews.")

            logger.info("Git collection finished.")

        elif source == 'jira':
            logger.info("Starting Jira collection...")
            connector = JiraCollector()
            issues = connector.collect()

            # Map Jira issues to the Issue model
            issue_data = [
                {
                    "id": issue["key"], # Using key as primary key
                    "issue_key": issue["key"],
                    "type": issue["issue_type"],
                    "status": issue["status"],
                    "title": issue["summary"],
                    "created_date": issue["created"],
                    "resolved_date": issue["resolved"],
                } for issue in issues
            ]

            if issue_data:
                bulk_upsert(session, Issue, issue_data)
                logger.info(f"Upserted {len(issue_data)} issues.")

            logger.info("Jira collection finished.")

        else:
            logger.warning(f"Unknown source: {source}")

    except Exception as e:
        logger.error(f"An error occurred processing job {job}: {e}")
        # Optionally, you could nack the message to requeue it
        # ch.basic_nack(delivery_tag=method.delivery_tag)
    finally:
        session.close()
        ch.basic_ack(delivery_tag=method.delivery_tag)
        logger.info(f"Finished processing job: {job}")


def main():
    rabbitmq_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
    channel = connection.channel()

    channel.queue_declare(queue='collection_jobs')

    channel.basic_consume(queue='collection_jobs', on_message_callback=callback)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    # A small delay to ensure RabbitMQ is fully up and running
    time.sleep(10)
    main()
