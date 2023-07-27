ARG BASE_IMAGE
FROM ${BASE_IMAGE}

# Install system-level packages
COPY packages.txt .
USER root
RUN if [[ -s packages.txt ]]; then \
    apt-get update && cat packages.txt | tr '\r\n' '\n' | sed -e 's/#.*//' | xargs apt-get install -y --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*; \
  fi

# Install python packages
COPY requirements.txt .
RUN if grep -Eqx 'apache-airflow\s*[=~>]{1,2}.*' requirements.txt; then \
    echo >&2 "Do not upgrade by specifying 'apache-airflow' in your requirements.txt, change the base image instead!";  exit 1; \
  fi; \
  pip install --no-cache-dir --root-user-action=ignore -r requirements.txt
USER astro