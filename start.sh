#!/bin/bash

# Astrologer Bot Startup Script
# This script helps you start the bot with proper configuration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}🌟 Astrologer Telegram Bot${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_status "Docker and Docker Compose are installed ✓"
}

# Check if .env file exists
check_env_file() {
    if [ ! -f "backend/.env" ]; then
        print_warning ".env file not found. Creating from template..."
        cp backend/.env.example backend/.env
        print_warning "Please edit backend/.env with your configuration before continuing."
        print_warning "Required: TELEGRAM_BOT_TOKEN, OPENROUTER_API_KEY"
        read -p "Press Enter after configuring .env file..."
    else
        print_status ".env file found ✓"
    fi
}

# Validate required environment variables
validate_env() {
    source backend/.env 2>/dev/null || true
    
    missing_vars=()
    
    if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
        missing_vars+=("TELEGRAM_BOT_TOKEN")
    fi
    
    if [ -z "$OPENROUTER_API_KEY" ]; then
        missing_vars+=("OPENROUTER_API_KEY")
    fi
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        print_error "Missing required environment variables:"
        for var in "${missing_vars[@]}"; do
            echo "  - $var"
        done
        print_error "Please configure these in backend/.env"
        exit 1
    fi
    
    print_status "Environment variables validated ✓"
}

# Start services
start_services() {
    print_status "Starting Astrologer Bot services..."
    
    # Build and start services
    docker-compose up --build -d
    
    print_status "Services started successfully!"
    print_status "Bot API: http://localhost:8000"
    print_status "Health check: http://localhost:8000/health"
}

# Show service status
show_status() {
    echo ""
    print_status "Service Status:"
    docker-compose ps
}

# Show logs
show_logs() {
    echo ""
    print_status "Recent logs (press Ctrl+C to exit):"
    docker-compose logs -f --tail=50
}

# Main menu
show_menu() {
    echo ""
    echo "Choose an option:"
    echo "1) Start bot (development mode)"
    echo "2) Start bot (production mode)"
    echo "3) Start with monitoring (Flower)"
    echo "4) Stop bot"
    echo "5) View logs"
    echo "6) View status"
    echo "7) Restart bot"
    echo "8) Clean restart (rebuild)"
    echo "9) Exit"
    echo ""
}

# Handle menu selection
handle_menu() {
    read -p "Enter your choice [1-9]: " choice
    
    case $choice in
        1)
            print_status "Starting in development mode..."
            docker-compose up --build -d
            show_status
            ;;
        2)
            print_status "Starting in production mode..."
            docker-compose --profile production up --build -d
            show_status
            ;;
        3)
            print_status "Starting with monitoring..."
            docker-compose --profile monitoring up --build -d
            show_status
            print_status "Flower monitoring: http://localhost:5555"
            ;;
        4)
            print_status "Stopping bot..."
            docker-compose down
            print_status "Bot stopped."
            ;;
        5)
            show_logs
            ;;
        6)
            show_status
            ;;
        7)
            print_status "Restarting bot..."
            docker-compose restart
            show_status
            ;;
        8)
            print_status "Clean restart (rebuilding)..."
            docker-compose down
            docker-compose up --build -d
            show_status
            ;;
        9)
            print_status "Goodbye!"
            exit 0
            ;;
        *)
            print_error "Invalid option. Please try again."
            ;;
    esac
}

# Main execution
main() {
    print_header
    
    # Initial checks
    check_docker
    check_env_file
    validate_env
    
    # If arguments provided, handle them
    if [ $# -gt 0 ]; then
        case $1 in
            "start")
                start_services
                show_status
                ;;
            "stop")
                docker-compose down
                print_status "Bot stopped."
                ;;
            "logs")
                show_logs
                ;;
            "status")
                show_status
                ;;
            "restart")
                docker-compose restart
                show_status
                ;;
            "clean")
                docker-compose down -v
                docker-compose up --build -d
                show_status
                ;;
            *)
                echo "Usage: $0 [start|stop|logs|status|restart|clean]"
                exit 1
                ;;
        esac
        exit 0
    fi
    
    # Interactive mode
    while true; do
        show_menu
        handle_menu
        echo ""
        read -p "Press Enter to continue..."
    done
}

# Run main function
main "$@"
