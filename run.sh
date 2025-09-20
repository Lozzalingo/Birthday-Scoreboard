#!/bin/bash

# Birthday Scoreboard Deployment Script
echo "🎉 Birthday Scoreboard Deployment Script"
echo "======================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create data directory if it doesn't exist
if [ ! -d "data" ]; then
    echo "📁 Creating data directory..."
    mkdir -p data
fi

# Function to start the application
start_app() {
    echo "🚀 Starting Birthday Scoreboard..."
    docker-compose up -d --build

    echo "⏳ Waiting for application to start..."
    sleep 10

    # Check if the application is running
    if docker-compose ps | grep -q "Up"; then
        echo "✅ Birthday Scoreboard is running!"
        echo ""
        echo "🌐 Application URLs:"
        echo "   Main Leaderboard: http://localhost:8080"
        echo "   Join Game: http://localhost:8080/join"
        echo "   Scan Page: http://localhost:8080/scan"
        echo "   Admin Panel: http://localhost:8080/admin"
        echo ""
        echo "📱 For mobile access, use your server's IP address instead of localhost"
        echo "   Example: http://YOUR_SERVER_IP:8080"
    else
        echo "❌ Failed to start application. Check logs with: docker-compose logs"
        exit 1
    fi
}

# Function to stop the application
stop_app() {
    echo "🛑 Stopping Birthday Scoreboard..."
    docker-compose down
    echo "✅ Application stopped."
}

# Function to restart the application
restart_app() {
    echo "🔄 Restarting Birthday Scoreboard..."
    docker-compose down
    docker-compose up -d --build
    echo "✅ Application restarted."
}

# Function to show logs
show_logs() {
    echo "📋 Showing application logs..."
    docker-compose logs -f
}

# Function to show status
show_status() {
    echo "📊 Application Status:"
    docker-compose ps
}

# Function to backup database
backup_db() {
    echo "💾 Creating database backup..."
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    BACKUP_FILE="backup_leaderboard_${TIMESTAMP}.db"

    if [ -f "data/leaderboard.db" ]; then
        cp "data/leaderboard.db" "data/${BACKUP_FILE}"
        echo "✅ Database backed up to: data/${BACKUP_FILE}"
    else
        echo "❌ No database file found to backup."
    fi
}

# Function to clean up
cleanup() {
    echo "🧹 Cleaning up..."
    docker-compose down --rmi all --volumes --remove-orphans
    echo "✅ Cleanup complete."
}

# Main menu
case "$1" in
    start)
        start_app
        ;;
    stop)
        stop_app
        ;;
    restart)
        restart_app
        ;;
    logs)
        show_logs
        ;;
    status)
        show_status
        ;;
    backup)
        backup_db
        ;;
    cleanup)
        cleanup
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|logs|status|backup|cleanup}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the Birthday Scoreboard application"
        echo "  stop    - Stop the application"
        echo "  restart - Restart the application"
        echo "  logs    - Show application logs (press Ctrl+C to exit)"
        echo "  status  - Show application status"
        echo "  backup  - Create a backup of the database"
        echo "  cleanup - Stop and remove all containers, images, and volumes"
        echo ""
        echo "Examples:"
        echo "  ./run.sh start    # Start the application"
        echo "  ./run.sh logs     # View logs"
        echo "  ./run.sh backup   # Backup database"
        exit 1
        ;;
esac