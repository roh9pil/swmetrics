# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install git first, as it's needed for some package installations if they were from git
# Also, it's good to have it available in the image for debugging.
# The original Dockerfile installed git, so we keep it.
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install dependencies
# This is done in a separate step to leverage Docker's layer caching.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code
COPY . .

# Install the application
# This will run setup.py and install the sma-collect command
RUN pip install .
