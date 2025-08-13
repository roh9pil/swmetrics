# Software Metrics Analyzer (SMA) Collector

## Overview

The Software Metrics Analyzer (SMA) Collector is a tool designed to measure the productivity and efficiency of software development teams. It collects data from various development sources like Git repositories and Jira projects, processes it, and stores it in a database for analysis and visualization.

This project uses a containerized architecture with Docker and Docker Compose, making it easy to set up and run.

## Architecture

The application consists of several services orchestrated by `docker-compose`:

-   **`postgres`**: A PostgreSQL database used to store all the collected metrics data.
-   **`rabbitmq`**: A message broker that queues data collection jobs.
-   **`grafana`**: A visualization platform used to create and display dashboards based on the collected data.
-   **`collector-worker`**: A background worker that listens for jobs from RabbitMQ, collects data from sources (like Jira, Git), and stores it in the PostgreSQL database.
-   **`sma-collector`**: A command-line tool that dispatches collection jobs to RabbitMQ. This is run manually to trigger the data collection process.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

-   [Docker](https://docs.docker.com/get-docker/)
-   [Docker Compose](https://docs.docker.com/compose/install/)

## How to Run

1.  **Clone the Repository**

    ```bash
    git clone https://github.com/your-repo/sma-collector.git
    cd sma-collector
    ```

2.  **Create Configuration File**

    Copy the example environment file `.env.example` to a new file named `.env`.

    ```bash
    cp .env.example .env
    ```

3.  **Configure Your Environment**

    Open the `.env` file and fill in the required values for your environment. You must provide credentials for the data sources you want to analyze (e.g., Jira, GitHub).

    **Key variables to configure:**
    -   `GIT_REPO_URL`: The URL of the remote Git repository you want to analyze.
    -   `JIRA_SERVER`, `JIRA_USERNAME`, `JIRA_API_TOKEN`, `JIRA_PROJECT_KEY`: Your Jira instance details.
    -   Other credentials for Jenkins, SonarQube, etc., if you use them.

4.  **Build and Start the Services**

    Run the following command to build the Docker images and start all the background services (`postgres`, `rabbitmq`, `grafana`, and `collector-worker`) in detached mode.

    ```bash
    docker-compose up --build -d
    ```
    The `collector-worker` service will start and wait for collection jobs to be dispatched.

5.  **Run the Data Collection**

    To start the data collection process, run the `sma-collector` service. This will send jobs to the `collector-worker`.

    ```bash
    docker-compose run --rm sma-collector
    ```

    You can run this command anytime you want to trigger a new data collection run.

## Accessing the Services

-   **Grafana Dashboard**:
    -   URL: `http://localhost:3001`
    -   Default Username: `admin`
    -   Default Password: `admin`
    You will need to configure a PostgreSQL data source in Grafana and build your own dashboards to visualize the data.

-   **RabbitMQ Management UI**:
    -   URL: `http://localhost:15672`
    -   Default Username: `user`
    -   Default Password: `password`
    Here you can monitor the message queues and see the flow of collection jobs.

-   **PostgreSQL Database**:
    -   The database is exposed on port `5433` on your host machine. You can connect to it using a database client if you need to inspect the data directly.
    -   Credentials are in your `.env` file (`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`).
