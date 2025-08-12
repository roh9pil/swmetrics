from setuptools import setup, find_packages

setup(
    name="sma_collector",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "python-dotenv",
        "pydantic-settings",
        "GitPython",
        "jira",
        "SQLAlchemy",
        "fastapi",
        "uvicorn[standard]",
        "pandas",
        "plotly",
        "dash",
    ],
    entry_points={
        'console_scripts': [
            'sma-collect=sma_collector.main:main',
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool to collect and visualize software development metrics.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/sma-collector",
)

