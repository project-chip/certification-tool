#! /usr/bin/env sh
set -e

if [ -f /app/app/main.py ]; then
    DEFAULT_MODULE_NAME=app.main
    RELOAD_PATH=/app/app
elif [ -f /app/main.py ]; then
    DEFAULT_MODULE_NAME=main
    RELOAD_PATH=/app
elif [ -f /app/backend/app/main.py ]; then
    # this is a special case for development
    # the working dir will be /app/backend
    RELOAD_PATH=/app/backend/app
    DEFAULT_MODULE_NAME=app.main
fi
MODULE_NAME=${MODULE_NAME:-$DEFAULT_MODULE_NAME}
VARIABLE_NAME=${VARIABLE_NAME:-app}
export APP_MODULE=${APP_MODULE:-"$MODULE_NAME:$VARIABLE_NAME"}

HOST=${HOST:-0.0.0.0}
PORT=${PORT:-80}
LOG_LEVEL=${LOG_LEVEL:-info}

# If there's a prestart.sh script in the /app directory or other path specified, run it before starting
DEFAULT_PRE_START_PATH="/app/prestart.sh"
if [ -f /app/app/prestart.sh ]; then
    DEFAULT_PRE_START_PATH="/app/app/prestart.sh"
elif [ -f /app/backend/prestart.sh ]; then
    DEFAULT_PRE_START_PATH="/app/backend/prestart.sh"
fi
PRE_START_PATH=${PRE_START_PATH:-$DEFAULT_PRE_START_PATH}
echo "Checking for script in $PRE_START_PATH"
if [ -f $PRE_START_PATH ] ; then
    echo "Running script $PRE_START_PATH"
    . "$PRE_START_PATH"
else 
    echo "There is no script $PRE_START_PATH"
fi

# Start Uvicorn with live reload
exec uvicorn --reload --reload-dir $RELOAD_PATH --host $HOST --port $PORT --log-level $LOG_LEVEL --ws-ping-timeout 60 "$APP_MODULE"
