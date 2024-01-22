#!/bin/bash

###############################################
###    This script is for local testing     ###
###    Make sure to create local env vars   ###
###    for the following:                   ###
### DYNATRACE_ENDPOINT="(url)/api/v2/otlp"  ###
### DYNATRACE_TOKEN="fffffffxxxxxxxxxxxxx"  ###
### BACKEND_URL="http://localhost:5000"     ###
###############################################

cleanup() {
  echo "Stopping Backend (PID: $BACKEND_PID)..."
  kill -TERM $BACKEND_PID
  echo "Stopping Frontend (PID: $FRONTEND_PID)..."
  kill -TERM $FRONTEND_PID
}

trap 'cleanup' SIGINT

# Start the backend
echo "Starting Backend..."
cd backend 
python3 backend.py 5002 & 
BACKEND_PID=$!
cd ..

# Start the frontend
echo "Starting Frontend..."
cd frontend 
python3 frontend.py 5001 &
FRONTEND_PID=$!

wait
