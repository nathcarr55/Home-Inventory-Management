# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV FLASK_APP run.py
ENV FLASK_RUN_HOST 0.0.0.0

# Set the working directory in the container to /BinGenie
WORKDIR /BinGenie

# Install system dependencies
RUN apt-get update \
  && apt-get install -y --no-install-recommends gcc \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /BinGenie/
RUN pip install --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /BinGenie
COPY . /BinGenie/

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run the application
CMD ["flask", "run"]
