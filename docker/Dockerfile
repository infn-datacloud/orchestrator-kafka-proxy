ARG PYTHON_VERSION=3.9
ARG POETRY_VERSION=1.8.3

# Create requirements.txt from poetry dependencies
FROM ghcr.io/withlogicco/poetry:${POETRY_VERSION}-python-${PYTHON_VERSION}-slim AS requirements

WORKDIR /tmp

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export \
    -f requirements.txt \
    --output requirements.txt \
    --without-hashes \
    --without dev


FROM python:${PYTHON_VERSION}-slim AS production

# Updating packages and installing libraries
RUN apt-get update \
    && apt-get clean

WORKDIR /app/

# Upgrade pip and install requirements
COPY --from=requirements /tmp/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip \
    && pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./app /app/app
COPY ./orchestrator_kafka_proxy.py /app/orchestrator_kafka_proxy.py

CMD ["python", "orchestrator_kafka_proxy.py"]
