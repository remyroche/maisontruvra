#!/bin/bash

# Script to check if Redis is running and start it if needed
# For macOS development environment

echo "=================================================="
echo "Redis Status Check for Maison Trüvra"
echo "=================================================="

# Function to check if Redis is running
check_redis() {
    if redis-cli ping > /dev/null 2>&1; then
        echo "✅ Redis is running and responding to ping"
        return 0
    else
        echo "❌ Redis is not responding"
        return 1
    fi
}

# Function to check if Redis is installed
check_redis_installed() {
    if command -v redis-server > /dev/null 2>&1; then
        echo "✅ Redis server is installed"
        return 0
    else
        echo "❌ Redis server is not installed"
        return 1
    fi
}

# Function to install Redis on macOS
install_redis_macos() {
    echo "Installing Redis using Homebrew..."
    if command -v brew > /dev/null 2>&1; then
        brew install redis
        echo "✅ Redis installed successfully"
    else
        echo "❌ Homebrew not found. Please install Homebrew first:"
        echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi
}

# Function to start Redis
start_redis() {
    echo "Starting Redis server..."
    
    # Try to start Redis as a service (macOS with Homebrew)
    if command -v brew > /dev/null 2>&1; then
        brew services start redis
        echo "✅ Redis started as a service"
    else
        # Start Redis manually
        redis-server --daemonize yes
        echo "✅ Redis started manually"
    fi
    
    # Wait a moment for Redis to start
    sleep 2
    
    # Check if it's running now
    if check_redis; then
        echo "✅ Redis is now running successfully"
    else
        echo "❌ Failed to start Redis"
        exit 1
    fi
}

# Main execution
echo "-> Checking Redis installation..."
if ! check_redis_installed; then
    echo "-> Redis not found. Installing..."
    install_redis_macos
fi

echo "-> Checking if Redis is running..."
if check_redis; then
    echo "-> Redis is already running. No action needed."
else
    echo "-> Redis is not running. Starting Redis..."
    start_redis
fi

echo ""
echo "Redis Status Summary:"
echo "====================="
redis-cli info server | grep "redis_version\|uptime_in_seconds\|tcp_port"

echo ""
echo "✅ Redis is ready for Maison Trüvra backend!"
echo "   - Cache: redis://localhost:6379/0"
echo "   - Celery: redis://localhost:6379/0"
echo ""
echo "To stop Redis later, run: brew services stop redis"