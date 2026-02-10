#!/bin/bash
set -e

echo "🌱 Seeding demo data..."

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "⚠️  DATABASE_URL not set, using default..."
    export DATABASE_URL="postgresql://finops:finops_dev_password@localhost:5432/finops_db"
fi

echo "🔍 Checking database connection..."
if ! psql "$DATABASE_URL" -c "SELECT 1" > /dev/null 2>&1; then
    echo "❌ Cannot connect to database. Make sure PostgreSQL is running."
    exit 1
fi

echo "✅ Database connection successful"

# Seed demo tenants
echo "👥 Creating demo tenants..."
psql "$DATABASE_URL" <<EOF
-- Create demo organization and tenant
INSERT INTO organizations (id, name, slug) 
VALUES ('org-demo', 'Demo Organization', 'demo-org')
ON CONFLICT (id) DO NOTHING;

INSERT INTO tenants (id, organization_id, name, slug) 
VALUES ('tenant-demo', 'org-demo', 'Demo Tenant', 'demo-tenant')
ON CONFLICT (id) DO NOTHING;

-- Create demo user
INSERT INTO users (id, email, name, tenant_id) 
VALUES ('user-demo', 'demo@example.com', 'Demo User', 'tenant-demo')
ON CONFLICT (id) DO NOTHING;
EOF

# Seed demo budgets
echo "💰 Creating demo budgets..."
psql "$DATABASE_URL" <<EOF
INSERT INTO budgets (id, tenant_id, name, amount, period, threshold_percentage) 
VALUES 
  ('budget-1', 'tenant-demo', 'Monthly Cloud Budget', 10000, 'monthly', 80),
  ('budget-2', 'tenant-demo', 'Q1 2026 Budget', 30000, 'quarterly', 90)
ON CONFLICT (id) DO NOTHING;
EOF

# Seed demo workflows
echo "🔄 Creating demo workflows..."
psql "$DATABASE_URL" <<EOF
INSERT INTO workflows (id, tenant_id, name, enabled, trigger_type) 
VALUES 
  ('workflow-1', 'tenant-demo', 'Budget Alert - Slack', true, 'budget.threshold_exceeded'),
  ('workflow-2', 'tenant-demo', 'Anomaly Detection', true, 'anomaly.cost_spike')
ON CONFLICT (id) DO NOTHING;
EOF

echo ""
echo "✅ Demo data seeded successfully!"
echo ""
echo "📋 Demo credentials:"
echo "   Email: demo@example.com"
echo "   Tenant: demo-tenant"
echo ""
