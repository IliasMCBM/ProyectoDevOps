#!/bin/bash

# Exit on error
set -e

echo "Starting application..."

# Start the application using docker-compose
docker-compose up -d

echo "Application started successfully!"
echo "Access the application at http://localhost:8501" 