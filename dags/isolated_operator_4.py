from datetime import datetime

from airflow.settings import conf
from airflow import DAG

from dags.extras import docs
from include.isolation import IsolatedOperator
from airflow.operators.bash import BashOperator

with DAG("isolated_operator_4", schedule=None, start_date=datetime(1970, 1, 1), doc_md=docs.doc):
    IsolatedOperator(
        task_id="example_bash",
        image="locahost:5000/data-team",
        operator=BashOperator,
        bash_command="echo hi",
        kubernetes_pod_operator_kwargs={
            "image_pull_policy": "Never",
            "kubernetes_conn_id": "kubernetes",
            "namespace": conf.get('kubernetes', 'NAMESPACE'),
        }
    )
