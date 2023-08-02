from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator, ExternalPythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator

from dags.extras import docs
from include.encryption import md5
from include.isolation import IsolatedOperator


def test_four_fn(task_instance):
    return md5(task_instance.dag_id)


def test_six_fn(a, b):
    print(a, b)
    if a == b:
        print("They match!")
        return True
    else:
        raise RuntimeError("They don't match!!!")


with DAG("isolated_operator_4", schedule=None, start_date=datetime(1970, 1, 1), doc_md=docs.doc):
    test_two = IsolatedOperator(
        task_id="test_two",
        doc_md="""We use SQLExecuteQueryOperator via IsolatedOperator""",
        image="localhost:5000/dependency-isolation-in-airflow_36d6b4/airflow/data-team",
        operator=PostgresOperator,
        sql="SELECT 1, '{{ ti.dag_id }}';",
        postgres_conn_id="PSQL",
        kubernetes_pod_operator_kwargs={
            "image_pull_policy": "Never",
            "kubernetes_conn_id": "KUBERNETES",
        }
    )

    # TODO - ERROR HERE. Python fn doesn't want to serialize
    test_four = IsolatedOperator(
        task_id="test_four",
        image="localhost:5000/dependency-isolation-in-airflow_36d6b4/airflow/data-team",
        doc_md="""We can call a function in this file, that can call a function in /include""",
        operator=PythonOperator,
        python_callable=test_four_fn,
        kubernetes_pod_operator_kwargs={
            "image_pull_policy": "Never",
            "kubernetes_conn_id": "KUBERNETES",
        }
    )

    test_five = IsolatedOperator(
        task_id="test_five",
        image="localhost:5000/dependency-isolation-in-airflow_36d6b4/airflow/py2",
        doc_md="""We can call a separate python2.7 and pass _some_ state in via Airflow Templates and argv""",
        operator=BashOperator,
        bash_command="""python2.7 dags/extras/py27_md5.py "{{ ti.dag_id }}" """,
        cwd="/usr/local/airflow",
        kubernetes_pod_operator_kwargs={
            "image_pull_policy": "Never",
            "kubernetes_conn_id": "KUBERNETES",
        }
    )


    # TODO - ERROR HERE. Python fn doesn't want to serialize
    def run_py27_md5():
        """Couldn't call it directly as that'd interfere with the DAG being parsed"""
        from dags.extras import py27_md5
        global virtualenv_string_args
        return py27_md5.main(virtualenv_string_args[0])


    test_five_b = IsolatedOperator(
        task_id="test_five_b",
        doc_md="""We can call py2.7 via the EPO, but we can't get airflow context templates :/ so partial failure""",
        image="localhost:5000/dependency-isolation-in-airflow_36d6b4/airflow/py2",
        operator=ExternalPythonOperator,
        python="/usr/bin/python2.7",
        python_callable=run_py27_md5,
        string_args=["{{ ti.dag_id }}"],
        expect_airflow=False,
        kubernetes_pod_operator_kwargs={
            "image_pull_policy": "Never",
            "kubernetes_conn_id": "KUBERNETES",
        }
    )

    test_six = PythonOperator(
        task_id="test_six",
        python_callable=test_six_fn,
        op_args=[test_four.output, test_five_b.output]
    )
