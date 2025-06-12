#!/bin/bash

# Database Management Script for Transcription System
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Check if .env file exists
check_env() {
    if [ ! -f .env ]; then
        print_error ".env file not found. Please copy .env.example to .env and configure it."
        exit 1
    fi
}

# Start the database
start_db() {
    print_status "Starting PostgreSQL database..."
    check_docker
    check_env
    
    docker-compose up -d postgres
    
    print_status "Waiting for database to be ready..."
    sleep 10
    
    if docker-compose exec postgres pg_isready -U "$(grep POSTGRES_USER .env | cut -d '=' -f2)" > /dev/null 2>&1; then
        print_success "Database is ready!"
        print_status "Database is running on port $(grep POSTGRES_PORT .env | cut -d '=' -f2)"
    else
        print_error "Database failed to start properly"
        exit 1
    fi
}

# Stop the database
stop_db() {
    print_status "Stopping PostgreSQL database..."
    docker-compose down
    print_success "Database stopped"
}

# Reset the database (WARNING: This will delete all data)
reset_db() {
    print_warning "This will delete ALL database data. Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        print_status "Stopping and removing database..."
        docker-compose down -v
        docker volume rm python-audio_postgres_data 2>/dev/null || true
        print_success "Database reset complete"
        print_status "Run './db.sh start' to recreate the database"
    else
        print_status "Database reset cancelled"
    fi
}

# Show database status
status_db() {
    check_env
    
    if docker-compose ps postgres | grep -q "Up"; then
        print_success "Database is running"
        
        # Try to connect and show basic info
        if command -v python3 > /dev/null 2>&1; then
            print_status "Testing database connection..."
            python3 -c "
import sys
sys.path.append('.')
from database import DatabaseManager
db = DatabaseManager()
if db.test_connection():
    print('✅ Database connection successful')
else:
    print('❌ Database connection failed')
" 2>/dev/null || print_warning "Could not test database connection (dependencies may not be installed)"
        fi
    else
        print_warning "Database is not running"
    fi
}

# Connect to database CLI
connect_db() {
    check_env
    source .env
    
    if ! docker-compose ps postgres | grep -q "Up"; then
        print_error "Database is not running. Run './db.sh start' first."
        exit 1
    fi
    
    print_status "Connecting to database CLI..."
    docker-compose exec postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"
}

# Show logs
logs_db() {
    print_status "Showing database logs (Ctrl+C to exit)..."
    docker-compose logs -f postgres
}

# Show help
show_help() {
    echo "Database Management Script for Transcription System"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start     Start the PostgreSQL database"
    echo "  stop      Stop the PostgreSQL database"
    echo "  restart   Restart the PostgreSQL database"
    echo "  status    Show database status"
    echo "  reset     Reset database (WARNING: Deletes all data)"
    echo "  connect   Connect to database CLI"
    echo "  logs      Show database logs"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start    # Start the database"
    echo "  $0 status   # Check if database is running"
    echo "  $0 connect  # Open psql CLI"
}

# Main script logic
case "${1:-help}" in
    start)
        start_db
        ;;
    stop)
        stop_db
        ;;
    restart)
        stop_db
        sleep 2
        start_db
        ;;
    status)
        status_db
        ;;
    reset)
        reset_db
        ;;
    connect)
        connect_db
        ;;
    logs)
        logs_db
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
