#! /usr/bin/env sh

# Let the DB start
python ./app/backend_pre_start.py

# Run migrations
alembic upgrade head

# Create initial data in DB
python ./app/initial_data.py

# Update SDK YAML tests
./scripts/fetch_sdk_yaml_tests_and_runner.sh
