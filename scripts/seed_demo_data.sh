#!/bin/bash
# Seed demo data for tenant-service
set -e

echo "===================================================="
echo "Seeding demo data for FinOps SaaS Platform"
echo "===================================================="

# Configuration
TENANT_SERVICE_URL="${TENANT_SERVICE_URL:-http://localhost:8002}"
API_VERSION="v1"
BASE_URL="$TENANT_SERVICE_URL/api/$API_VERSION"

# Mock headers for authentication (replace with real tokens in production)
HEADERS=(
    -H "Content-Type: application/json"
    -H "X-User-ID: seed-user-001"
    -H "X-Request-ID: seed-$(date +%s)"
)

echo ""
echo "1. Creating Organizations..."
echo "----------------------------"

# Create Acme Corp
ORG1_RESPONSE=$(curl -s -X POST "$BASE_URL/orgs" \
    "${HEADERS[@]}" \
    -d '{
        "name": "Acme Corporation",
        "description": "Leading provider of cloud solutions",
        "industry": "Technology",
        "settings": {
            "timezone": "America/New_York",
            "currency": "USD"
        }
    }')
ORG1_ID=$(echo "$ORG1_RESPONSE" | jq -r '.id')
echo "✓ Created Acme Corporation (ID: $ORG1_ID)"

# Create TechStart Inc
ORG2_RESPONSE=$(curl -s -X POST "$BASE_URL/orgs" \
    "${HEADERS[@]}" \
    -d '{
        "name": "TechStart Inc",
        "description": "Innovative startup in fintech",
        "industry": "Financial Services",
        "settings": {
            "timezone": "America/Los_Angeles",
            "currency": "USD"
        }
    }')
ORG2_ID=$(echo "$ORG2_RESPONSE" | jq -r '.id')
echo "✓ Created TechStart Inc (ID: $ORG2_ID)"

# Create Global Enterprises
ORG3_RESPONSE=$(curl -s -X POST "$BASE_URL/orgs" \
    "${HEADERS[@]}" \
    -d '{
        "name": "Global Enterprises",
        "description": "Worldwide retail and logistics",
        "industry": "Retail",
        "settings": {
            "timezone": "Europe/London",
            "currency": "GBP"
        }
    }')
ORG3_ID=$(echo "$ORG3_RESPONSE" | jq -r '.id')
echo "✓ Created Global Enterprises (ID: $ORG3_ID)"

echo ""
echo "2. Creating Tenants..."
echo "----------------------"

# Tenants for Acme Corp
TENANT1_RESPONSE=$(curl -s -X POST "$BASE_URL/tenants" \
    -H "Content-Type: application/json" \
    -H "X-Org-ID: $ORG1_ID" \
    -H "X-User-ID: seed-user-001" \
    -d '{
        "name": "Production",
        "description": "Production environment",
        "settings": {"env": "prod"}
    }')
TENANT1_ID=$(echo "$TENANT1_RESPONSE" | jq -r '.id')
echo "✓ Created Acme Corp - Production (ID: $TENANT1_ID)"

TENANT2_RESPONSE=$(curl -s -X POST "$BASE_URL/tenants" \
    -H "Content-Type: application/json" \
    -H "X-Org-ID: $ORG1_ID" \
    -H "X-User-ID: seed-user-001" \
    -d '{
        "name": "Staging",
        "description": "Staging environment",
        "settings": {"env": "staging"}
    }')
TENANT2_ID=$(echo "$TENANT2_RESPONSE" | jq -r '.id')
echo "✓ Created Acme Corp - Staging (ID: $TENANT2_ID)"

TENANT3_RESPONSE=$(curl -s -X POST "$BASE_URL/tenants" \
    -H "Content-Type: application/json" \
    -H "X-Org-ID: $ORG1_ID" \
    -H "X-User-ID: seed-user-001" \
    -d '{
        "name": "Development",
        "description": "Development environment",
        "settings": {"env": "dev"}
    }')
TENANT3_ID=$(echo "$TENANT3_RESPONSE" | jq -r '.id')
echo "✓ Created Acme Corp - Development (ID: $TENANT3_ID)"

# Tenants for TechStart Inc
TENANT4_RESPONSE=$(curl -s -X POST "$BASE_URL/tenants" \
    -H "Content-Type: application/json" \
    -H "X-Org-ID: $ORG2_ID" \
    -H "X-User-ID: seed-user-001" \
    -d '{
        "name": "Platform",
        "description": "Main platform tenant",
        "settings": {"env": "prod"}
    }')
TENANT4_ID=$(echo "$TENANT4_RESPONSE" | jq -r '.id')
echo "✓ Created TechStart Inc - Platform (ID: $TENANT4_ID)"

# Tenants for Global Enterprises
TENANT5_RESPONSE=$(curl -s -X POST "$BASE_URL/tenants" \
    -H "Content-Type: application/json" \
    -H "X-Org-ID: $ORG3_ID" \
    -H "X-User-ID: seed-user-001" \
    -d '{
        "name": "EMEA",
        "description": "Europe, Middle East, and Africa region",
        "settings": {"region": "emea"}
    }')
TENANT5_ID=$(echo "$TENANT5_RESPONSE" | jq -r '.id')
echo "✓ Created Global Enterprises - EMEA (ID: $TENANT5_ID)"

TENANT6_RESPONSE=$(curl -s -X POST "$BASE_URL/tenants" \
    -H "Content-Type: application/json" \
    -H "X-Org-ID: $ORG3_ID" \
    -H "X-User-ID: seed-user-001" \
    -d '{
        "name": "APAC",
        "description": "Asia-Pacific region",
        "settings": {"region": "apac"}
    }')
TENANT6_ID=$(echo "$TENANT6_RESPONSE" | jq -r '.id')
echo "✓ Created Global Enterprises - APAC (ID: $TENANT6_ID)"

echo ""
echo "3. Creating Cloud Accounts..."
echo "------------------------------"

# AWS accounts for Acme Corp
curl -s -X POST "$BASE_URL/cloud-accounts" \
    -H "Content-Type: application/json" \
    -H "X-Org-ID: $ORG1_ID" \
    -H "X-User-ID: seed-user-001" \
    -d "{
        \"name\": \"Acme AWS Production\",
        \"provider\": \"aws\",
        \"account_id\": \"123456789012\",
        \"tenant_id\": \"$TENANT1_ID\",
        \"account_name\": \"acme-prod\",
        \"settings\": {\"region\": \"us-east-1\"}
    }" > /dev/null
echo "✓ Created AWS account for Acme Corp Production"

curl -s -X POST "$BASE_URL/cloud-accounts" \
    -H "Content-Type: application/json" \
    -H "X-Org-ID: $ORG1_ID" \
    -H "X-User-ID: seed-user-001" \
    -d "{
        \"name\": \"Acme AWS Staging\",
        \"provider\": \"aws\",
        \"account_id\": \"123456789013\",
        \"tenant_id\": \"$TENANT2_ID\",
        \"account_name\": \"acme-staging\",
        \"settings\": {\"region\": \"us-east-1\"}
    }" > /dev/null
echo "✓ Created AWS account for Acme Corp Staging"

# Azure account for Acme Corp
curl -s -X POST "$BASE_URL/cloud-accounts" \
    -H "Content-Type: application/json" \
    -H "X-Org-ID: $ORG1_ID" \
    -H "X-User-ID: seed-user-001" \
    -d "{
        \"name\": \"Acme Azure Production\",
        \"provider\": \"azure\",
        \"account_id\": \"aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee\",
        \"tenant_id\": \"$TENANT1_ID\",
        \"account_name\": \"acme-azure-prod\",
        \"settings\": {\"location\": \"eastus\"}
    }" > /dev/null
echo "✓ Created Azure account for Acme Corp Production"

# GCP account for TechStart Inc
curl -s -X POST "$BASE_URL/cloud-accounts" \
    -H "Content-Type: application/json" \
    -H "X-Org-ID: $ORG2_ID" \
    -H "X-User-ID: seed-user-001" \
    -d "{
        \"name\": \"TechStart GCP Platform\",
        \"provider\": \"gcp\",
        \"account_id\": \"techstart-platform-123456\",
        \"tenant_id\": \"$TENANT4_ID\",
        \"account_name\": \"techstart-platform\",
        \"settings\": {\"region\": \"us-central1\"}
    }" > /dev/null
echo "✓ Created GCP account for TechStart Inc"

# Multi-cloud for Global Enterprises
curl -s -X POST "$BASE_URL/cloud-accounts" \
    -H "Content-Type: application/json" \
    -H "X-Org-ID: $ORG3_ID" \
    -H "X-User-ID: seed-user-001" \
    -d "{
        \"name\": \"Global EMEA AWS\",
        \"provider\": \"aws\",
        \"account_id\": \"987654321098\",
        \"tenant_id\": \"$TENANT5_ID\",
        \"account_name\": \"global-emea\",
        \"settings\": {\"region\": \"eu-west-1\"}
    }" > /dev/null
echo "✓ Created AWS account for Global Enterprises EMEA"

curl -s -X POST "$BASE_URL/cloud-accounts" \
    -H "Content-Type: application/json" \
    -H "X-Org-ID: $ORG3_ID" \
    -H "X-User-ID: seed-user-001" \
    -d "{
        \"name\": \"Global APAC AWS\",
        \"provider\": \"aws\",
        \"account_id\": \"987654321099\",
        \"tenant_id\": \"$TENANT6_ID\",
        \"account_name\": \"global-apac\",
        \"settings\": {\"region\": \"ap-southeast-1\"}
    }" > /dev/null
echo "✓ Created AWS account for Global Enterprises APAC"

echo ""
echo "4. Creating Persona Views..."
echo "-----------------------------"

# Executive views
curl -s -X POST "$BASE_URL/views" \
    -H "Content-Type: application/json" \
    -H "X-Org-ID: $ORG1_ID" \
    -H "X-User-ID: seed-user-001" \
    -d '{
        "name": "Executive Dashboard",
        "persona": "executive",
        "description": "High-level cost overview for executives",
        "config": {
            "widgets": [
                {"type": "total_cost", "period": "monthly"},
                {"type": "cost_trend", "period": "6months"},
                {"type": "top_services", "limit": 5},
                {"type": "budget_status"}
            ],
            "filters": {"granularity": "monthly"}
        },
        "is_default": true,
        "is_shared": true
    }' > /dev/null
echo "✓ Created Executive Dashboard for Acme Corp"

# FinOps views
curl -s -X POST "$BASE_URL/views" \
    -H "Content-Type: application/json" \
    -H "X-Org-ID: $ORG1_ID" \
    -H "X-User-ID: seed-user-001" \
    -d '{
        "name": "FinOps Cost Analysis",
        "persona": "finops",
        "description": "Detailed cost analysis and optimization opportunities",
        "config": {
            "widgets": [
                {"type": "cost_breakdown", "groupBy": ["service", "region"]},
                {"type": "anomalies", "sensitivity": "high"},
                {"type": "recommendations", "category": "all"},
                {"type": "ri_coverage"},
                {"type": "savings_plan_coverage"}
            ],
            "filters": {"granularity": "daily"}
        },
        "is_default": true,
        "is_shared": true
    }' > /dev/null
echo "✓ Created FinOps Cost Analysis for Acme Corp"

# Engineering views
curl -s -X POST "$BASE_URL/views" \
    -H "Content-Type: application/json" \
    -H "X-Org-ID: $ORG1_ID" \
    -H "X-User-ID: seed-user-001" \
    -d '{
        "name": "Engineering Resources",
        "persona": "engineering",
        "description": "Infrastructure costs by team and project",
        "config": {
            "widgets": [
                {"type": "cost_by_tag", "tag": "team"},
                {"type": "cost_by_tag", "tag": "project"},
                {"type": "resource_utilization"},
                {"type": "idle_resources"}
            ],
            "filters": {"granularity": "daily", "groupBy": "resource"}
        },
        "is_default": true,
        "is_shared": true
    }' > /dev/null
echo "✓ Created Engineering Resources view for Acme Corp"

# Product Ops views
curl -s -X POST "$BASE_URL/views" \
    -H "Content-Type: application/json" \
    -H "X-Org-ID: $ORG2_ID" \
    -H "X-User-ID: seed-user-001" \
    -d '{
        "name": "Product Unit Economics",
        "persona": "product_ops",
        "description": "Cost per user, per transaction, and other unit economics",
        "config": {
            "widgets": [
                {"type": "unit_cost", "metric": "cost_per_user"},
                {"type": "unit_cost", "metric": "cost_per_transaction"},
                {"type": "cost_trend_by_product"},
                {"type": "product_margin"}
            ],
            "filters": {"granularity": "daily"}
        },
        "is_default": true,
        "is_shared": true
    }' > /dev/null
echo "✓ Created Product Unit Economics view for TechStart Inc"

# Custom tenant admin view
curl -s -X POST "$BASE_URL/views" \
    -H "Content-Type: application/json" \
    -H "X-Org-ID: $ORG3_ID" \
    -H "X-User-ID: seed-user-001" \
    -d '{
        "name": "Regional Cost Summary",
        "persona": "tenant_admin",
        "description": "Cost summary by region for multi-region deployment",
        "config": {
            "widgets": [
                {"type": "cost_by_region"},
                {"type": "cost_by_tenant"},
                {"type": "cross_region_data_transfer"},
                {"type": "regional_recommendations"}
            ],
            "filters": {"granularity": "weekly", "groupBy": "region"}
        },
        "is_default": true,
        "is_shared": true
    }' > /dev/null
echo "✓ Created Regional Cost Summary for Global Enterprises"

echo ""
echo "===================================================="
echo "✅ Demo data seeding completed successfully!"
echo "===================================================="
echo ""
echo "Summary:"
echo "  - 3 Organizations"
echo "  - 6 Tenants"
echo "  - 6 Cloud Accounts (AWS, Azure, GCP)"
echo "  - 5 Persona Views"
echo ""
echo "You can now explore the tenant-service API at:"
echo "  $TENANT_SERVICE_URL/docs"
echo ""
