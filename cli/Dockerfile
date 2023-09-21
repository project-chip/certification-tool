
FROM ubuntu:22.04

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y python3-pip python3-venv libpq-dev curl 

RUN ln -s /usr/bin/python3.10 /usr/local/bin/python

# Use /cli to host cli source
WORKDIR /cli/
ENV PYTHONPATH=/cli

# Install Poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

# Allow installing dev dependencies to run tests
# Copy poetry dependecy files and install dependencies
# We copy install dependencies before copying all cli source to reuse the dependency install step in docker.
COPY pyproject.toml poetry.lock /cli/
ARG INSTALL_DEV=true
RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install --no-root ; else poetry install --no-root --no-dev ; fi"
