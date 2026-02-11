#!/bin/bash
# ============================================================================
# FinOps SaaS - Database Migrations Script
# Runs Alembic migrations to set up and update the database schema
# ============================================================================

set -e  # Exit on error

# Colors for output
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ALEMBIC_DIR="$PROJECT_ROOT/data/db/alembic"

echo -e "${BLUE}FinOps SaaS - Database Migrations${NC}"
echo ""

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    # Try to load from .env
    if [ -f "$PROJECT_ROOT/.env" ]; then
        echo -e "${YELLOW}Loading DATABASE_URL from .env file...${NC}"
        export $(grep -v '^#' "$PROJECT_ROOT/.env" | grep DATABASE_URL | xargs)
    fi
    
    # If still not set, use default
    if [ -z "$DATABASE_URL" ]; then
        echo -e "${YELLOW}DATABASE_URL not set, using default...${NC}"
        export DATABASE_URL="postgresql://finops:finops_dev@localhost:5432/finops"
    fi
fi

echo -e "${GREEN}Database URL:${NC} ${DATABASE_URL//:*@/:***@}"  # Mask password
echo ""

# Change to alembic directory
cd "$ALEMBIC_DIR"

# Check if alembic is installed
if ! command -v alembic &> /dev/null; then
    echo -e "${RED}Error: Alembic is not installed${NC}"
    echo "Install it with: pip install alembic psycopg2-binary"
    exit 1
fi

# Parse command line arguments
COMMAND=${1:-upgrade}
TARGET=${2:-head}

case "$COMMAND" in
    upgrade)
        echo -e "${GREEN}Running database migrations (upgrade to $TARGET)...${NC}"
        alembic upgrade "$TARGET"
        echo ""
        echo -e "${GREEN}✓ Migrations completed successfully${NC}"
        ;;
    
    downgrade)
        echo -e "${YELLOW}Downgrading database to $TARGET...${NC}"
        echo -e "${RED}WARNING: This may result in data loss!${NC}"
        read -p "Are you sure you want to continue? (yes/no): " confirm
        if [ "$confirm" = "yes" ]; then
            alembic downgrade "$TARGET"
            echo ""
            echo -e "${GREEN}✓ Downgrade completed${NC}"
        else
            echo "Aborted."
            exit 0
        fi
        ;;
    
    current)
        echo -e "${GREEN}Current database revision:${NC}"
        alembic current
        ;;
    
    history)
        echo -e "${GREEN}Migration history:${NC}"
        alembic history --verbose
        ;;
    
    heads)
        echo -e "${GREEN}Head revisions:${NC}"
        alembic heads
        ;;
    
    show)
        if [ -z "$TARGET" ]; then
            echo -e "${RED}Error: Please specify a revision to show${NC}"
            echo "Usage: $0 show <revision>"
            exit 1
        fi
        echo -e "${GREEN}Showing migration: $TARGET${NC}"
        alembic show "$TARGET"
        ;;
    
    stamp)
        if [ -z "$TARGET" ]; then
            echo -e "${RED}Error: Please specify a revision to stamp${NC}"
            echo "Usage: $0 stamp <revision>"
            exit 1
        fi
        echo -e "${YELLOW}Stamping database at revision: $TARGET${NC}"
        alembic stamp "$TARGET"
        echo -e "${GREEN}✓ Database stamped${NC}"
        ;;
    
    revision)
        MESSAGE=${TARGET:-"new migration"}
        echo -e "${GREEN}Creating new migration: $MESSAGE${NC}"
        alembic revision --autogenerate -m "$MESSAGE"
        echo -e "${GREEN}✓ Migration file created${NC}"
        ;;
    
    help|--help|-h)
        echo "Usage: $0 [command] [target]"
        echo ""
        echo "Commands:"
        echo "  upgrade [target]   - Upgrade database to target revision (default: head)"
        echo "  downgrade [target] - Downgrade database to target revision"
        echo "  current            - Show current database revision"
        echo "  history            - Show migration history"
        echo "  heads              - Show head revisions"
        echo "  show <revision>    - Show details of a specific migration"
        echo "  stamp <revision>   - Stamp database with a specific revision (without running migrations)"
        echo "  revision <message> - Create a new migration file"
        echo "  help               - Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0                      # Run all migrations (upgrade to head)"
        echo "  $0 upgrade              # Same as above"
        echo "  $0 upgrade 001          # Upgrade to revision 001"
        echo "  $0 downgrade -1         # Downgrade by one revision"
        echo "  $0 current              # Show current revision"
        echo "  $0 history              # Show migration history"
        echo ""
        echo "Environment Variables:"
        echo "  DATABASE_URL - PostgreSQL connection string"
        echo "                 (default: postgresql://finops:finops_dev@localhost:5432/finops)"
        ;;
    
    *)
        echo -e "${RED}Error: Unknown command '$COMMAND'${NC}"
        echo "Run '$0 help' for usage information"
        exit 1
        ;;
esac

echo ""
echo -e "${BLUE}Done.${NC}"
