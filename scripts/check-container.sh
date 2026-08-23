#!/usr/bin/env bash
set -e

IMAGE_NAME="opspilot-api:local-security"

echo "Building API image..."
docker build --target api -t "$IMAGE_NAME" .

echo "Scanning API image with Trivy..."
docker run --rm \
    -v /var/run/docker.sock:/var/run/docker.sock \
    aquasec/trivy:0.74.0 \
    image \
    --scanners vuln \
    --severity HIGH,CRITICAL \
    --ignore-unfixed \
    --exit-code 1 \
    "$IMAGE_NAME"

echo "Container security check passed."