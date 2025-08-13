import os
import pika
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """
    Dispatches data collection jobs to the RabbitMQ queue.
    """
    logger.info("=================================================")
    logger.info("  Software Metrics Analyzer (SMA) Job Dispatcher")
    logger.info("=================================================")

    rabbitmq_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
        channel = connection.channel()
        channel.queue_declare(queue='collection_jobs')
        logger.info("Successfully connected to RabbitMQ.")
    except pika.exceptions.AMQPConnectionError as e:
        logger.error(f"Failed to connect to RabbitMQ: {e}")
        return

    # Define the jobs to be dispatched
    jobs = [
        {'source': 'git'},
        {'source': 'jira'}
        # Add other sources like 'bitbucket', 'swarm' here as you migrate them
    ]

    for job in jobs:
        message = json.dumps(job)
        channel.basic_publish(
            exchange='',
            routing_key='collection_jobs',
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))
        logger.info(f" [x] Sent job: {message}")

    connection.close()
    logger.info("All collection jobs have been dispatched.")
    logger.info("=================================================")


if __name__ == "__main__":
    main()