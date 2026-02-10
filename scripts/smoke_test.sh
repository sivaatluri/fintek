#!/bin/bash
set -e

echo "🧪 Running smoke tests..."

# Check if services are running
check_service() {
    local name=$1
    local url=$2
    local expected_status=${3:-200}
    
    echo "🔍 Checking $name..."
    
    if response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>&1); then
        if [ "$response" = "$expected_status" ]; then
            echo "   ✅ $name is responding (HTTP $response)"
            return 0
        else
            echo "   ⚠️  $name returned HTTP $response (expected $expected_status)"
            return 1
        fi
    else
        echo "   ❌ $name is not accessible"
        return 1
    fi
}

# Test infrastructure services
echo "📦 Testing infrastructure services..."
check_service "MinIO" "http://localhost:9000/minio/health/live"
check_service "Prometheus" "http://localhost:9090/-/healthy"
check_service "Grafana" "http://localhost:3003/api/health"
check_service "MailHog" "http://localhost:8025"

echo ""

# Test application services (if running)
echo "🚀 Testing application services..."
if docker ps | grep -q finops-gateway; then
    check_service "Gateway API" "http://localhost:3000/health" || true
fi

if docker ps | grep -q finops-web; then
    check_service "Web UI" "http://localhost:3001" || true
fi

echo ""

# Test database connectivity
echo "🗄️  Testing database connectivity..."
if docker exec finops-postgres pg_isready -U finops > /dev/null 2>&1; then
    echo "   ✅ PostgreSQL is accessible"
else
    echo "   ❌ PostgreSQL is not accessible"
fi

if docker exec finops-redis redis-cli ping > /dev/null 2>&1; then
    echo "   ✅ Redis is accessible"
else
    echo "   ❌ Redis is not accessible"
fi

echo ""
echo "✅ Smoke tests completed!"
echo ""
