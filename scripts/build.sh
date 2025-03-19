#!/bin/bash

# Exit on error
set -e

echo "Starting build process..."

# Build the Docker image
docker-compose build

echo "Build completed successfully!" 