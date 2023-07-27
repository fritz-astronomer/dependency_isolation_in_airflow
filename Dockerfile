# syntax=quay.io/astronomer/airflow-extensions:v1
FROM quay.io/astronomer/astro-runtime:8.7.0

PYENV 3.10 data-science environments/data-team/requirements.txt
