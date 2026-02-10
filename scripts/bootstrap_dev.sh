#!/bin/bash
set -e

echo "🚀 Bootstrapping development environment..."

# Check prerequisites
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed. Aborting." >&2; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose is required but not installed. Aborting." >&2; exit 1; }

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "✅ .env file created. Please update with your configuration."
fi

# Start infrastructure services
echo "🐳 Starting infrastructure services..."
docker-compose -f docker-compose.tools.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check PostgreSQL
echo "🔍 Checking PostgreSQL..."
until docker exec finops-postgres pg_isready -U finops > /dev/null 2>&1; do
    echo "   Waiting for PostgreSQL..."
    sleep 2
done
echo "✅ PostgreSQL is ready"

# Check Redis
echo "🔍 Checking Redis..."
until docker exec finops-redis redis-cli ping > /dev/null 2>&1; do
    echo "   Waiting for Redis..."
    sleep 2
done
echo "✅ Redis is ready"

# Check MinIO
echo "🔍 Checking MinIO..."
until curl -sf http://localhost:9000/minio/health/live > /dev/null 2>&1; do
    echo "   Waiting for MinIO..."
    sleep 2
done
echo "✅ MinIO is ready"

echo ""
echo "✨ Development environment bootstrapped successfully!"
echo ""
echo "📍 Services available at:"
echo "   - PostgreSQL: localhost:5432"
echo "   - Redis: localhost:6379"
echo "   - MinIO Console: http://localhost:9001 (minioadmin/minioadmin)"
echo "   - Kafka: localhost:9092"
echo "   - Prometheus: http://localhost:9090"
echo "   - Grafana: http://localhost:3003 (admin/admin)"
echo "   - Keycloak: http://localhost:8081 (admin/admin)"
echo "   - MailHog: http://localhost:8025"
echo ""
echo "🎯 Next steps:"
echo "   1. Run: make migrate     # Run database migrations"
echo "   2. Run: make seed        # Seed demo data"
echo "   3. Run: make dev         # Start application services"
echo ""
