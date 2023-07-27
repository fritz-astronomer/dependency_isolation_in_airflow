from datetime import datetime

from airflow.settings import conf
from airflow import DAG

from dags.extras import docs
from include.isolation import IsolatedOperator
from airflow.operators.bash import BashOperator

with DAG("kpo_3", schedule=None, start_date=datetime(1970, 1, 1), doc_md=docs.doc):
    pass
