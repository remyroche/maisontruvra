#!/bin/bash

# A simple script to start the development environment for Maison Trüvra.

# --- Configuration ---
FLASK_APP_PATH="manage.py"
FLASK_DEBUG_MODE=1
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
        echo "Please ensure it is installed in your virtual environment and try again."
        if [ "$1" == "python3" ]; then
            echo "To install dependencies, run: pip install -r backend/requirements.txt"
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

# Install/update dependencies
echo "-> Installing/updating backend dependencies..."
if [ -d "$VENV_PATH" ]; then
    # If venv exists and was activated, 'pip' will be the correct one from the PATH.
    pip install -r backend/requirements.txt
else
    # If no venv, warn the user and try with the system pip3.
    echo "   Warning: Installing dependencies globally. It is highly recommended to use a virtual environment."
    pip3 install -r backend/requirements.txt
fi

# Trap SIGINT (Ctrl+C) and call cleanup
trap cleanup SIGINT

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
