#!/bin/bash

# Exit on error
set -e

echo "Starting release process..."

# Get version from git tag or use default
VERSION=${1:-$(git describe --tags --always)}
echo "Releasing version: $VERSION"

# Tag the Docker image
docker tag rag-app:latest rag-app:$VERSION

# Save the image
docker save rag-app:$VERSION > "release/rag-app-$VERSION.tar"

echo "Release completed successfully!" 