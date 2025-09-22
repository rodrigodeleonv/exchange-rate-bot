#!/bin/bash

# =============================================================================
# Exchange Rate Bot - Production Deploy Script
# =============================================================================
# Automates the complete production deployment process
# Configures permissions, volume structure and executes docker compose
# =============================================================================

set -e  # Exit if any command fails

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions with colors
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Banner
echo -e "${BLUE}"
echo "=================================================="
echo "  Exchange Rate Bot - Production Deploy"
echo "=================================================="
echo -e "${NC}"

# 1. Verify we are in the correct directory
log_info "Verifying project directory..."
if [ ! -f "compose.yml" ] || [ ! -f "Dockerfile" ]; then
    log_error "compose.yml or Dockerfile not found"
    log_error "Make sure to run this script from the project root"
    exit 1
fi
log_success "Project directory verified"

# 2. Verify required configuration files exist
log_info "Verifying required configuration..."
if [ ! -f ".env" ]; then
    log_error ".env file not found"
    log_error "Create .env file with required environment variables before deployment"
    exit 1
fi
log_success "Configuration files verified"

# 3. Create volume structure if it doesn't exist
log_info "Creating volume structure..."
mkdir -p .volumes/logs .volumes/data
log_success "Volume structure created: .volumes/{logs,data}"

# 4. Configure correct permissions and detect user IDs
log_info "Configuring volume permissions and detecting user IDs..."
# Get current user UID and GID
USER_ID=$(id -u)
GROUP_ID=$(id -g)
log_info "Current user: UID=$USER_ID, GID=$GROUP_ID"

# Export for docker-compose build args
export USER_ID
export GROUP_ID

# Configure permissions so container can write
chmod -R 755 .volumes/
log_success "Permissions configured correctly"
log_info "Docker will build container with UID=$USER_ID, GID=$GROUP_ID"

# 5. Stop existing containers if running
log_info "Stopping existing containers..."
if docker compose ps -q | grep -q .; then
    docker compose down
    log_success "Existing containers stopped"
else
    log_info "No containers currently running"
fi

# 6. Clean orphaned Docker images (optional)
log_info "Cleaning orphaned Docker images..."
docker image prune -f > /dev/null 2>&1 || true
log_success "Cleanup completed"

# 7. Build and deploy
log_info "Starting build and deployment..."
echo -e "${YELLOW}This may take a few minutes...${NC}"

# Build with current user UID/GID and deploy
if docker compose build --build-arg USER_ID=$USER_ID --build-arg GROUP_ID=$GROUP_ID && \
   docker compose up -d; then
    log_success "Deployment completed successfully!"

    # 8. Show service status
    echo ""
    log_info "Service status:"
    docker compose ps

    # 9. Show initial logs
    echo ""
    log_info "Initial logs (last 10 lines):"
    docker compose logs --tail=10

    # 10. Useful information
    echo ""
    echo -e "${GREEN}=================================================="
    echo "  🚀 Deployment Complete"
    echo "=================================================="
    echo -e "${NC}"
    echo "📊 Real-time logs: docker compose logs -f"
    echo "🛑 Stop services: docker compose down"
    echo ""
    echo "📁 Local volumes:"
    echo "   - Logs: .volumes/logs/"
    echo "   - Data: .volumes/data/"
    echo ""

else
    log_error "Deployment failed!"
    echo ""
    log_info "Showing error logs:"
    docker compose logs --tail=20
    exit 1
fi
