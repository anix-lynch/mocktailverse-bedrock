# Production-ready Docker image for AWS ETL Pipeline
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    AIRFLOW_HOME=/opt/airflow \
    AIRFLOW__CORE__LOAD_EXAMPLES=False

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Create airflow user
RUN useradd -ms /bin/bash -d ${AIRFLOW_HOME} airflow

# Install Python dependencies
COPY requirements-full.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements-full.txt && rm /tmp/requirements-full.txt

# Create necessary directories
RUN mkdir -p ${AIRFLOW_HOME}/dags ${AIRFLOW_HOME}/logs ${AIRFLOW_HOME}/plugins

# Copy application code
COPY --chown=airflow:airflow airflow_dag.py ${AIRFLOW_HOME}/dags/
COPY --chown=airflow:airflow dbt_project/ ${AIRFLOW_HOME}/dbt_project/
COPY --chown=airflow:airflow lambda/ /opt/lambda/
COPY --chown=airflow:airflow glue_job.py /opt/glue/
COPY --chown=airflow:airflow streamlit_app.py ${AIRFLOW_HOME}/
COPY --chown=airflow:airflow margarita_recipes.json ${AIRFLOW_HOME}/data/

# Copy entrypoint script
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Change ownership to airflow user
RUN chown -R airflow:airflow ${AIRFLOW_HOME}

# Switch to airflow user
USER airflow

# Set working directory
WORKDIR ${AIRFLOW_HOME}

# Expose ports
EXPOSE 8080 8501

# Default entrypoint
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["airflow", "webserver"]
