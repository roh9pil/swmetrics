-- Phase 1 Tables
CREATE TABLE IF NOT EXISTS commits (
    sha VARCHAR(40) PRIMARY KEY,
    author_name VARCHAR(255),
    author_email VARCHAR(255),
    authored_date TIMESTAMP WITH TIME ZONE,
    message TEXT
);

CREATE TABLE IF NOT EXISTS issues (
    id VARCHAR(255) PRIMARY KEY,
    issue_key VARCHAR(255) UNIQUE,
    type VARCHAR(100),
    status VARCHAR(100),
    title TEXT,
    created_date TIMESTAMP WITH TIME ZONE,
    resolved_date TIMESTAMP WITH TIME ZONE,
    lead_time_minutes INT
);

CREATE TABLE IF NOT EXISTS builds (
    id VARCHAR(255) PRIMARY KEY,
    job_name VARCHAR(255),
    number INT,
    status VARCHAR(100),
    start_time TIMESTAMP WITH TIME ZONE,
    finish_time TIMESTAMP WITH TIME ZONE,
    duration_millis BIGINT
);

CREATE TABLE IF NOT EXISTS build_commits (
    build_id VARCHAR(255) REFERENCES builds(id),
    commit_sha VARCHAR(40) REFERENCES commits(sha),
    PRIMARY KEY (build_id, commit_sha)
);

CREATE TABLE IF NOT EXISTS deployments (
    id VARCHAR(255) PRIMARY KEY REFERENCES builds(id),
    commit_sha VARCHAR(40),
    start_time TIMESTAMP WITH TIME ZONE,
    finish_time TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS incidents (
    id VARCHAR(255) PRIMARY KEY REFERENCES issues(id),
    deployment_id VARCHAR(255) REFERENCES deployments(id),
    created_date TIMESTAMP WITH TIME ZONE,
    resolved_date TIMESTAMP WITH TIME ZONE
);

-- Phase 2 Tables
ALTER TABLE issues ADD COLUMN IF NOT EXISTS sli INT;

CREATE TABLE IF NOT EXISTS vts_runs (
    id VARCHAR(255) PRIMARY KEY,
    run_name VARCHAR(255),
    test_plan VARCHAR(255),
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    total_tests INT,
    passed_tests INT,
    failed_tests INT,
    pass_rate FLOAT
);

CREATE TABLE IF NOT EXISTS osp_metrics (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE,
    device_id VARCHAR(255),
    metric_name VARCHAR(255),
    metric_value FLOAT,
    source VARCHAR(255)
);

-- Phase 3 Tables
CREATE TABLE IF NOT EXISTS team_surveys (
    id SERIAL PRIMARY KEY,
    survey_date DATE NOT NULL,
    team_name VARCHAR(255) NOT NULL,
    satisfaction_score FLOAT,
    UNIQUE (survey_date, team_name)
);

CREATE TABLE IF NOT EXISTS code_reviews (
    id VARCHAR(255) PRIMARY KEY,
    repo_name VARCHAR(255),
    pr_number INT,
    title TEXT,
    author VARCHAR(255),
    created_date TIMESTAMP WITH TIME ZONE,
    merged_date TIMESTAMP WITH TIME ZONE,
    first_comment_date TIMESTAMP WITH TIME ZONE,
    time_to_first_review_minutes INT,
    time_to_merge_minutes INT,
    comment_count INT
);

CREATE TABLE IF NOT EXISTS code_quality_metrics (
    id SERIAL PRIMARY KEY,
    analysis_date DATE NOT NULL,
    project_key VARCHAR(255) NOT NULL,
    metric_name VARCHAR(255) NOT NULL,
    metric_value FLOAT,
    UNIQUE (analysis_date, project_key, metric_name)
);

