#!/bin/bash
# Check health of all services

echo "🏥 Fintek Health Check"
echo ""

services=("gateway:8000" "auth:8001" "tenant:8002" "ingestion:8003" "workflows:8004" "budgets:8005" "query:8006" "integrations:8007")

all_healthy=true

for service in "${services[@]}"; do
    IFS=':' read -r name port <<< "$service"
    
    response=$(curl -s http://localhost:$port/health)
    status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$port/health)
    
    if [ "$status" = "200" ]; then
        echo "✅ $name - Healthy"
    else
        echo "❌ $name - Unhealthy (HTTP $status)"
        all_healthy=false
    fi
done

echo ""

if [ "$all_healthy" = true ]; then
    echo "✅ All services are healthy!"
    exit 0
else
    echo "⚠️  Some services are unhealthy"
    exit 1
fi
