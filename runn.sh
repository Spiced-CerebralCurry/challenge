#!/bin/bash

# to stop on first error
set -e

# Delete older .pyc files if desired
# find . -type d \( -name env -o -name venv  \) -prune -false -o -name "*.pyc" -exec rm -rf {} \;

# Run required migrations
export FLASK_APP=core/server.py

# Uncomment these lines if you need migrations:
# flask db init -d core/migrations/
# flask db migrate -m "Initial migration." -d core/migrations/
# flask db upgrade -d core/migrations/

# Detect OS to decide between waitress (Windows) vs gunicorn (Unix)

##OS_NAME="$(uname -s)"

##if [[ "$OS_NAME" == "CYGWIN" ]] || [[ "$OS_NAME" == "MINGW" ]] || [[ "$OS_NAME" == "MSYS" ]] || [[ "$OS_NAME" == "NT" ]]; then
    echo "Detected Windows environment. Using Waitress..."
    
    # Run the app using Waitress
    waitress-serve --port=5000 core.server:app
##else
    ##echo "Detected Unix-based environment (Linux/Mac). Using Gunicorn..."
    
    # Run the app using Gunicorn
    ##gunicorn -c gunicorn_config.py core.server:app
##fi