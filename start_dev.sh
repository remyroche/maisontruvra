#!/bin/bash

# A simple script to start the development environment for Maison Trüvra.
# Updated to use Playwright for PDF generation to avoid Homebrew issues on pre-release macOS.

# --- Configuration ---
FLASK_APP_PATH="manage.py"
FLASK_DEBUG_MODE=1

CODEQL_SARIF_OUTPUT="codeql_audit_results.sarif"
CODEQL_DATABASE_DIR="codeql_db_for_flask"

VITE_CONFIG_PATH="website/vite.config.js"
VENV_PATH="venv" # Common name for virtual environment folder

# --- Functions ---
print_header() {
    echo "=================================================="
    echo "Maison Trüvra Development Environment Setup & Launch"
    echo "=================================================="
}

activate_venv() {
    echo "-> Searching for Python virtual environment..."
    if [ -d "$VENV_PATH" ]; then
        echo "   Virtual environment found. Activating..."
        source "$VENV_PATH/bin/activate"
    else
        echo "   Warning: Virtual environment '$VENV_PATH' not found."
        echo "   Assuming required Python packages are installed in the global environment."
    fi
}

check_command() {
    if ! command -v $1 &> /dev/null
    then
        echo "Error: Command '$1' is not found."
        echo "Please ensure it is installed and in your PATH."
        if [ "$1" == "python3" ]; then
            echo "To install Python dependencies, run: pip install -r backend/requirements.txt"
        fi
        exit 1
    fi
}

start_flask_backend() {
    echo "-> Starting Flask backend..."
    export FLASK_APP=$FLASK_APP_PATH
    export FLASK_DEBUG=$FLASK_DEBUG_MODE
    # Using 'python -m flask' is often more reliable than just 'flask'
    python3 -m flask run --port=5000 &
    FLASK_PID=$!
    echo "   Flask backend started with PID: $FLASK_PID"
}

# This function replaces the previous WeasyPrint/Homebrew installation.
# Playwright downloads its own self-contained browser binaries, avoiding system dependencies.
install_playwright_deps() {
    echo "-> Checking and installing Playwright browser binaries..."
    echo "   (This might take a moment on the first run...)"

    # This command downloads the necessary browser binaries (e.g., Chromium).
    # It is run via 'python3 -m' to use the Playwright version from the virtual environment.
    # Make sure 'playwright' is listed in your backend/requirements.txt
    python3 -m playwright install --with-deps
    if [ $? -ne 0 ]; then
        echo "   [ERROR] Failed to install Playwright browsers."
        echo "   Please check the output above for errors and ensure 'playwright' is in requirements.txt."
        exit 1
    else
        echo "   Playwright browsers are installed."
    fi
}


start_vite_frontend() {
    echo "-> Starting Vite frontend dev server..."
    # Ensure frontend dependencies are installed
    if [ ! -d "website/node_modules" ]; then
        echo "   'node_modules' not found. Running 'npm install'..."
        (cd website && npm install)
    fi
    # Use a subshell for changing directory, and `exec` to replace the subshell
    # process with `npm`. This ensures $! gives us the PID of `npm`, not the subshell.
    (cd website && exec npm run dev) &
    VITE_PID=$!
    echo "   Vite frontend started with PID: $VITE_PID"
}

cleanup() {
    echo ""
    echo "-> Shutting down development servers..."
    # Kill the process group of each server to ensure child processes are also terminated.
    # The '-' before the PID signifies killing the process group.
    echo "   Stopping Flask (PID: $FLASK_PID) and Vite (PID: $VITE_PID)..."
    if [ -n "$FLASK_PID" ]; then kill -TERM -$FLASK_PID 2>/dev/null; fi
    if [ -n "$VITE_PID" ]; then kill -TERM -$VITE_PID 2>/dev/null; fi
    echo "   Shutdown complete."
    exit
}

# --- Main Execution ---
print_header

# Activate Virtual Environment
activate_venv

# Check for necessary tools
echo "-> Checking for necessary tools..."
check_command python3
check_command npm

# Check for libmagic (dependency for python-magic) on macOS
if [[ "$(uname)" == "Darwin" ]]; then
    if ! brew list libmagic &>/dev/null; then
        echo "   ❌ 'libmagic' is not installed via Homebrew. This is required by the 'python-magic' package."
        read -p "   Would you like to install it now? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "   Installing libmagic..."
            brew install libmagic
        else
            echo "   Skipping installation. The application might fail to start."
        fi
    fi
fi

# Check Redis
echo "-> Checking Redis status..."
if ! redis-cli ping > /dev/null 2>&1; then
    echo "   ❌ Redis is not running. Attempting to start it..."
    if [ -f "./check_redis.sh" ]; then
        # Make sure the helper script is executable
        chmod +x ./check_redis.sh
        # Run the helper script
        ./check_redis.sh
        # Check again after attempting to start
        if ! redis-cli ping > /dev/null 2>&1; then
            echo "   ❌ Failed to start Redis automatically. Please check the output above and start Redis manually."
            exit 1
        fi
    else
        echo "   ❌ 'check_redis.sh' not found. Please start Redis manually."
        echo "   - On macOS with Homebrew: brew services start redis"
        echo "   - On Ubuntu: sudo systemctl start redis-server"
        exit 1
    fi
fi
echo "   ✅ Redis is running."

# Install/update dependencies
echo "-> Installing/updating backend dependencies..."
echo "   NOTE: Ensure 'playwright' is in backend/requirements.txt and 'weasyprint' is removed."
if [ -d "$VENV_PATH" ]; then
    # If venv exists and was activated, 'pip' will be the correct one from the PATH.
    pip install -r backend/requirements.txt || { echo "   ❌ Failed to install Python dependencies. Aborting."; exit 1; }
else
    # If no venv, warn the user and try with the system pip3.
    echo "   Warning: Installing dependencies globally. It is highly recommended to use a virtual environment."
    pip3 install -r backend/requirements.txt || { echo "   ❌ Failed to install Python dependencies. Aborting."; exit 1; }
fi
echo "   ✅ Backend dependencies are up to date."

# Trap SIGINT (Ctrl+C) and call cleanup
trap cleanup SIGINT

# Install Playwright browser dependencies.
install_playwright_deps

# Start servers
start_flask_backend
start_vite_frontend

echo ""
echo "Development environment is running."
echo "Flask backend is on http://localhost:5000"
echo "Vite frontend is on http://localhost:5173 (or as specified in vite.config.js)"
echo "Press Ctrl+C to stop both servers."

# Wait indefinitely until script is interrupted
wait
