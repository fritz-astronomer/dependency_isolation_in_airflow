import os
from datetime import datetime

from airflow import DAG
from airflow.decorators import task
from airflow.operators.bash import BashOperator
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator

from dags.extras import docs
from include.encryption import md5


def test_four_fn(task_instance):
    return md5(task_instance.dag_id)


def test_six_fn(a, b):
    print(a, b)
    if a == b:
        print("They match!")
        return True
    else:
        raise RuntimeError("They don't match!!!")


with DAG("kpo_3", schedule=None, start_date=datetime(1970, 1, 1), doc_md=docs.doc) as dag:
    test_one = BashOperator(
        task_id="test_one",
        doc_md="""unable to do that, without reimplementing IsolatedOperator or similar""",
        bash_command="exit 1"
    )


    @task.kubernetes(
        image="python:slim",
        kubernetes_conn_id="KUBERNETES",
        doc_md="we can use a python image, pass our templates in as env_vars, "
               "and install providers-postgres at runtime",
        env_vars={
            "AIRFLOW_CONN_PSQL": "{{ conn.PSQL.get_uri() }}",
            "DAG_ID": '{{ ti.dag_id }}'
        }
    )
    def test_one_b():
        import subprocess
        import shlex
        import json

        subprocess.run(shlex.split("pip install apache-airflow-providers-postgres==5.5.2"), shell=True)

        from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

        with open("/airflow/xcom/return.json", 'w') as xcom:
            results = SQLExecuteQueryOperator(
                task_id="test_one",
                doc_md="""We use SQLExecuteQueryOperator""",
                sql=f"SELECT 1, '{os.getenv('DAG_ID', '')}';",
                conn_id="PSQL",
            ).execute({})
            xcom.write(json.dumps(results))


    test_two = BashOperator(
        task_id="test_two",
        doc_md="""unable to do that, without reimplementing IsolatedOperator or similar""",
        bash_command="exit 1"
    )


    @task.kubernetes(
        image="python:slim",
        kubernetes_conn_id="KUBERNETES",
        doc_md="Unable to implement - airflow is not installing correctly, reimplementing IsolatedOp",
        env_vars={
            "AIRFLOW_CONN_PSQL": "{{ conn.PSQL.get_uri() }}",
            "DAG_ID": '{{ ti.dag_id }}'
        },
        do_xcom_push=True,
        is_delete_operator_pod=False,
    )
    def test_two_b():
        raise RuntimeError("unable to implement")

        import sys
        import subprocess
        import shlex
        subprocess.run(
            shlex.split("pip install apache-airflow==2.6.1 apache-airflow-providers-postgres==3.0.0"),
            shell=True
        )

        def _exec():
            from airflow.providers.postgres.operators.postgres import PostgresOperator
            from airflow.providers_manager import ProvidersManager
            print(f"My python version is {sys.version}")
            for key, provider in ProvidersManager().providers.items():
                if key == 'apache-airflow-providers-postgres':
                    print(f"My postgres provider version is {provider.version}")

            with open("/airflow/xcom/return.json", 'w') as xcom:
                result = PostgresOperator(
                    task_id="ISOLATED_TASK",
                    sql=f"""SELECT 1, '{os.getenv('DAG_ID')}';""",
                    postgres_conn_id="PSQL"
                ).execute({})
                # The old PSQL operator doesn't actually ever return an xcom
                # so nothing to write :/
        _exec()
    test_two_b()

    test_three = KubernetesPodOperator(
        task_id="test_three",
        kubernetes_conn_id="KUBERNETES",
        doc_md="""We can use a ruby image easily""",
        image="ruby",
        cmds=["bash"],
        log_events_on_failure=True,
        arguments=[
            '-c',
            """mkdir -p /airflow/xcom/ && touch /airflow/xcom/return.json && """
            """ruby -e 'puts "{\\\"return_value\\\": \\\"Hello world {{ ti.dag_id }}\\\"}"' """
            """ > /airflow/xcom/return.json"""
        ],
        do_xcom_push=True,
    )

    test_four = BashOperator(
        task_id="test_four",
        doc_md="""unable to do that, without reimplementing IsolatedOperator or similar""",
        bash_command="exit 1"
    )

    @task.kubernetes(
        image="python:slim",
        kubernetes_conn_id="KUBERNETES",
        doc_md="Unable to do this without a volume - can't share /include",
    )
    def test_four_b():
        raise RuntimeError("unable to implement")


    test_five = BashOperator(
        task_id="test_five",
        doc_md="""unable to do that, without reimplementing IsolatedOperator or similar""",
        bash_command="exit 1"
    )

    test_six = BashOperator(
        task_id="test_six",
        doc_md="""unable to do that, without reimplementing IsolatedOperator or similar""",
        bash_command="exit 1"
    )
