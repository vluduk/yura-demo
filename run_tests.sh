#!/bin/bash

# Test Runner Script for Backend Unit Tests
# This script provides convenient shortcuts for running different test suites

set -e  # Exit on error

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

# Check if backend service is running
if ! docker compose ps backend | grep -q "Up"; then
    print_warning "Backend service is not running. Starting services..."
    docker compose up -d
    sleep 3
fi

# Main test commands
case "${1:-all}" in
    all)
        print_info "Running all tests..."
        docker compose exec backend python manage.py test --verbosity=2
        ;;
    
    models)
        print_info "Running model tests..."
        docker compose exec backend python manage.py test api.tests.test_models --verbosity=2
        ;;
    
    views)
        print_info "Running view tests..."
        docker compose exec backend python manage.py test api.tests.test_views --verbosity=2
        ;;
    
    serializers)
        print_info "Running serializer tests..."
        docker compose exec backend python manage.py test api.tests.test_serializers --verbosity=2
        ;;
    
    services)
        print_info "Running service tests..."
        docker compose exec backend python manage.py test api.tests.test_services --verbosity=2
        ;;
    
    auth)
        print_info "Running authentication tests..."
        docker compose exec backend python manage.py test api.tests.test_auth --verbosity=2
        ;;
    
    advisor)
        print_info "Running advisor tests..."
        docker compose exec backend python manage.py test api.tests.test_advisor --verbosity=2
        ;;
    
    coverage)
        print_info "Running tests with coverage..."
        docker compose exec backend coverage run --source='.' manage.py test
        docker compose exec backend coverage report
        print_info "Generating HTML coverage report..."
        docker compose exec backend coverage html
        print_info "Coverage report generated in htmlcov/"
        ;;
    
    quick)
        print_info "Running quick test suite (no verbosity)..."
        docker compose exec backend python manage.py test
        ;;
    
    help)
        echo "Backend Test Runner"
        echo ""
        echo "Usage: ./run_tests.sh [command]"
        echo ""
        echo "Commands:"
        echo "  all          - Run all tests (default)"
        echo "  models       - Run model tests only"
        echo "  views        - Run view tests only"
        echo "  serializers  - Run serializer tests only"
        echo "  services     - Run service tests only"
        echo "  auth         - Run authentication tests only"
        echo "  advisor      - Run advisor tests only"
        echo "  coverage     - Run tests with coverage report"
        echo "  quick        - Run all tests without verbose output"
        echo "  help         - Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./run_tests.sh              # Run all tests"
        echo "  ./run_tests.sh models       # Run only model tests"
        echo "  ./run_tests.sh coverage     # Run with coverage report"
        ;;
    
    *)
        print_error "Unknown command: $1"
        echo "Run './run_tests.sh help' for usage information"
        exit 1
        ;;
esac

print_info "Tests completed!"
