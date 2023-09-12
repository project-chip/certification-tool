#! /usr/bin/env sh
set -e

if [ -f /app/app/main.py ]; then
    DEFAULT_MODULE_NAME=app.main
elif [ -f /app/main.py ]; then
    DEFAULT_MODULE_NAME=main
elif [ -f /app/backend/main.py ]; then
    # this is a special case for development
    # the working dir will be /app/backend
    DEFAULT_MODULE_NAME=main
fi
MODULE_NAME=${MODULE_NAME:-$DEFAULT_MODULE_NAME}
VARIABLE_NAME=${VARIABLE_NAME:-app}
export APP_MODULE=${APP_MODULE:-"$MODULE_NAME:$VARIABLE_NAME"}

if [ -f /app/gunicorn_conf.py ]; then
    DEFAULT_GUNICORN_CONF=/app/gunicorn_conf.py
elif [ -f /app/app/gunicorn_conf.py ]; then
    DEFAULT_GUNICORN_CONF=/app/app/gunicorn_conf.py
elif [ -f /app/backend/gunicorn_conf.py ]; then
    # this is a special case for development
    DEFAULT_GUNICORN_CONF=/app/backend/gunicorn_conf.py
else
    DEFAULT_GUNICORN_CONF=/gunicorn_conf.py
fi
export GUNICORN_CONF=${GUNICORN_CONF:-$DEFAULT_GUNICORN_CONF}
export WORKER_CLASS=${WORKER_CLASS:-"uvicorn.workers.UvicornWorker"}

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

# Start Gunicorn
exec gunicorn -k "$WORKER_CLASS" -c "$GUNICORN_CONF" "$APP_MODULE"