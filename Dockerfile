# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV FLASK_APP run.py
ENV FLASK_RUN_HOST 0.0.0.0

# Set the working directory in the container to /app
WORKDIR /app

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY BinGenie/ /app/

# Expose the port the app runs on
EXPOSE 8001

# Run the application with Gunicorn
CMD ["gunicorn", "--workers", "5", "--bind", "0.0.0.0:8001", "run:app"]
