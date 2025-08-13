from setuptools import setup, find_packages
import os

def parse_requirements(filename):
    """Load requirements from a pip requirements file."""
    with open(filename, 'r') as f:
        lines = (line.strip() for line in f)
        return [line for line in lines if line and not line.startswith('#')]

# Read the contents of the README file
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

install_requires = parse_requirements('requirements.txt')

setup(
    name="sma_collector",
    version="0.1.0",
    packages=find_packages(),
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'sma-collect=sma_collector.main:main',
        ],
    },
    author="SMA Collector Team",
    author_email="team@example.com",
    description="A tool to collect and visualize software development metrics.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-repo/sma-collector",
)
