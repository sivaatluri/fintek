#!/bin/bash
# Start all services with docker-compose

echo "🚀 Starting Fintek platform..."
echo ""

docker-compose up -d

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 10

echo ""
echo "✅ Services status:"
echo ""

services=("gateway:8000" "auth:8001" "tenant:8002" "ingestion:8003" "workflows:8004" "budgets:8005" "query:8006" "integrations:8007")

for service in "${services[@]}"; do
    IFS=':' read -r name port <<< "$service"
    status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$port/health || echo "000")
    if [ "$status" = "200" ]; then
        echo "✅ $name (http://localhost:$port) - Healthy"
    else
        echo "⚠️  $name (http://localhost:$port) - Not ready (HTTP $status)"
    fi
done

echo ""
echo "📊 Infrastructure:"
echo "  - PostgreSQL: localhost:5432"
echo "  - Redis: localhost:6379"
echo "  - Kafka: localhost:9092"
echo "  - Trino: http://localhost:8080"
echo "  - MinIO Console: http://localhost:9001"
echo ""
echo "📚 API Documentation:"
echo "  - Gateway: http://localhost:8000/docs"
echo ""
echo "🌐 Frontend:"
echo "  Run 'cd apps/web && npm install && npm run dev'"
echo "  Visit http://localhost:5173"
echo ""
