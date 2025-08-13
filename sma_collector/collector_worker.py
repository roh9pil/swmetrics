
import os
import pika
import json
import time
from sma_collector.connectors.git_connector import GitConnector
from sma_collector.connectors.jira_connector import JiraCollector
from sma_collector.config import settings

def callback(ch, method, properties, body):
    job = json.loads(body)
    print(f" [x] Received job: {job}")

    source = job.get('source')

    if source == 'git':
        print("Starting Git collection...")
        connector = GitConnector(
            repo_path=settings.GIT_REPO_PATH,
            repo_url=settings.GIT_REPO_URL,
            github_token=settings.GITHUB_TOKEN
        )
        connector.collect()
        print("Git collection finished.")
    elif source == 'jira':
        print("Starting Jira collection...")
        connector = JiraCollector()
        connector.collect()
        print("Jira collection finished.")
    # Add other collectors here in the future

    ch.basic_ack(delivery_tag=method.delivery_tag)


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
