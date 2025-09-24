#!/bin/bash

# =============================================================================
# Docker Entrypoint Script
# =============================================================================
# Runs database migrations before starting the application
# =============================================================================

set -e

echo "🚀 Starting Exchange Rate Bot..."

# Wait a moment for any database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 2

# Run database migrations
echo "🔄 Running database migrations..."
if alembic upgrade head; then
    echo "✅ Database migrations completed successfully"
else
    echo "❌ Database migrations failed"
    exit 1
fi

# Show current migration status
echo "📊 Current database revision:"
if ! alembic current 2>/tmp/alembic_error.log; then
    echo "❌ Unable to retrieve database revision - check database connection and alembic configuration"
    echo "Alembic error output:"
    cat /tmp/alembic_error.log
    rm -f /tmp/alembic_error.log
else
    echo "✅ Database revision retrieved successfully"
fi

# Execute the main command
echo "🎯 Starting application: $*"
exec "$@"
