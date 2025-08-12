from setuptools import setup, find_packages
import os

# Get the absolute path to the directory containing setup.py
setup_dir = os.path.abspath(os.path.dirname(__file__))

# Read the contents of the README file, which is in the parent directory
with open(os.path.join(setup_dir, '..', 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="sma_collector",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "python-dotenv",
        "pydantic-settings",
        "GitPython",
        "PyGithub",
        "atlassian-python-api",
        "jira",
        "requests",
        "SQLAlchemy",
        "fastapi",
        "uvicorn[standard]",
        "pandas",
        "plotly",
        "dash",
        "pytest",
    ],
    entry_points={
        'console_scripts': [
            'sma-collect=sma_collector.main:main',
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool to collect and visualize software development metrics.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/sma-collector",
)
