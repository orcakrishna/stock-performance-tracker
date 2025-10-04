#!/bin/bash

# Stop Stock Tracker Script

echo "Stopping Stock Tracker..."

# Kill all streamlit processes running app.py
pkill -f "streamlit run app.py"

# Kill the startup script if running
pkill -f "start_app.sh"

echo "Stock Tracker stopped."
