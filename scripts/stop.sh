#!/bin/bash
# Stop all services

echo "🛑 Stopping Fintek platform..."
docker-compose down

echo "✅ All services stopped"
