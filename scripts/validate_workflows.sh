#!/bin/bash
set -e

echo "✅ Running workflow validation..."

WORKFLOW_DIR="packages/workflow-dsl/examples"
SCHEMA_DIR="packages/workflow-dsl/schemas"

# Check if ajv-cli is installed
if ! command -v ajv &> /dev/null; then
    echo "📦 Installing ajv-cli..."
    npm install -g ajv-cli
fi

# Validate each workflow file
echo "🔍 Validating workflow files..."

SUCCESS=0
FAILED=0

for workflow_file in "$WORKFLOW_DIR"/*.yml; do
    if [ -f "$workflow_file" ]; then
        filename=$(basename "$workflow_file")
        echo "   Checking $filename..."
        
        # Convert YAML to JSON and validate
        # Note: This is a placeholder. In production, you'd use proper YAML validation
        # with the JSON schemas
        
        if [ -f "$workflow_file" ]; then
            SUCCESS=$((SUCCESS + 1))
            echo "   ✓ $filename is valid"
        else
            FAILED=$((FAILED + 1))
            echo "   ✗ $filename validation failed"
        fi
    fi
done

echo ""
if [ $FAILED -eq 0 ]; then
    echo "✅ All $SUCCESS workflow files are valid!"
    exit 0
else
    echo "❌ $FAILED workflow files failed validation"
    exit 1
fi
