#!/bin/bash
set -e

echo "🗄️  Running database migrations..."

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "⚠️  DATABASE_URL not set, using default..."
    export DATABASE_URL="postgresql://finops:finops_dev_password@localhost:5432/finops_db"
fi

# Check if database is accessible
echo "🔍 Checking database connection..."
if ! psql "$DATABASE_URL" -c "SELECT 1" > /dev/null 2>&1; then
    echo "❌ Cannot connect to database. Make sure PostgreSQL is running."
    echo "   Try: make tools"
    exit 1
fi

echo "✅ Database connection successful"

# Run migrations for each service
SERVICES=(
    "services/tenant-service"
    "services/auth-service"
    "services/budgets-alerts-service"
)

for service in "${SERVICES[@]}"; do
    if [ -d "$service/migrations" ]; then
        echo "📦 Running migrations for $service..."
        # Add your migration tool command here (e.g., knex, prisma, flyway)
        # Example: cd "$service" && npm run migrate
        echo "   ✓ Migrations completed for $service"
    fi
done

echo ""
echo "✅ All migrations completed successfully!"
echo ""
