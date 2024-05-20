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
<<<<<<< Updated upstream
  && apt-get install -y --no-install-recommends gcc \
=======
  && apt-get install -y --no-install-recommends \
     gcc \
     libpq-dev \
     build-essential \
     python3-dev \
     libxml2-dev \
     libxslt1-dev \
     zlib1g-dev \
     libffi-dev \
     libssl-dev \
     git \
>>>>>>> Stashed changes
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /BinGenie/
RUN pip install --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /BinGenie
COPY . /BinGenie/

# Expose the port the app runs on
EXPOSE 8000

# Run the application with Gunicorn
CMD ["gunicorn", "--workers", "5", "--bind", "0.0.0.0:8000", "run:app"]
