#!/bin/bash
# deploy/scripts/prod-validate.sh - Validate production image

set -e

echo "🔍 Validating production images..."

# Check image sizes (should be < 500MB for Python services)
for image in api worker sim-core; do
    size=$(docker images cbms-${image}:latest --format "{{.Size}}" 2>/dev/null || echo "N/A")
    echo "  ${image}: ${size}"
done

# Scan for vulnerabilities
echo ""
echo "🔒 Vulnerability scan (using Trivy)..."
docker run --rm \
    -v /var/run/docker.sock:/var/run/docker.sock \
    aquasec/trivy:latest image --severity HIGH,CRITICAL cbms-api:latest

# Run smoke tests
echo ""
echo "🧪 Smoke tests..."
docker compose -f deploy/docker-compose.yml run --rm api python -c "
from cbms_api.api.main import app
print('API imports OK')
"

docker compose -f deploy/docker-compose.yml run --rm worker python -c "
from cbms_workers.celery_app import celery_app
print('Worker imports OK')
"

echo ""
echo "✅ Validation complete"
