#!/bin/bash

# Stock Tracker Startup Script
# This script keeps the app running and restarts it if it crashes

APP_DIR="/Users/krishnashukla/Desktop/nse/CascadeProjects/windsurf-project"
LOG_DIR="$APP_DIR/logs"
VENV_PATH="$APP_DIR/venv"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Function to start the app
start_app() {
    echo "Starting Stock Tracker at $(date)" >> "$LOG_DIR/startup.log"
    
    # Activate virtual environment and run streamlit
    cd "$APP_DIR"
    source "$VENV_PATH/bin/activate"
    
    # Run streamlit in the background
    streamlit run app.py --server.port 8501 --server.headless true >> "$LOG_DIR/app.log" 2>&1 &
    
    echo "Stock Tracker started. Access at http://localhost:8501"
    echo "Logs available at: $LOG_DIR/app.log"
}

# Function to check if app is running
is_running() {
    pgrep -f "streamlit run app.py" > /dev/null
    return $?
}

# Main loop - keeps app running
while true; do
    if ! is_running; then
        echo "App not running. Starting..." >> "$LOG_DIR/startup.log"
        start_app
    fi
    
    # Check every 30 seconds
    sleep 30
done
