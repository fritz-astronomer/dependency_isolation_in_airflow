from datetime import datetime

from airflow import DAG
from airflow.decorators import task
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

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


with DAG("vanilla_airflow_1", schedule=None, start_date=datetime(1970, 1, 1), doc_md=docs.doc) as dag:
    test_one = SQLExecuteQueryOperator(
        task_id="test_one",
        doc_md="""We use SQLExecuteQueryOperator""",
        sql="SELECT 1, '{{ ti.dag_id }}';",
        conn_id="PSQL",
    )

    test_two = BashOperator(
        task_id="test_two",
        doc_md="""unable to do that, without reimplementing EPO/venv""",
        bash_command="exit 1"
    )

    # noinspection DuplicatedCode
    test_three = BashOperator(
        task_id="test_three",
        doc_md="""We can call ruby separately""",
        bash_command="""ruby -e 'puts "Hello world {{ ti.dag_id }}"'"""
    )

    test_four = PythonOperator(
        task_id="test_four",
        doc_md="""We can call a function in this file, that can call a function in /include""",
        python_callable=test_four_fn
    )

    @task.python(doc_md="Just to show off the Taskflow style")
    def test_four_b_task(task_instance=None):
        """We can, of course, do other stuff in here.
        We can also take an existing function and task-flow-ify it
        like: `test_four_b = task(test_four_fn)(...)`"""
        return test_four_fn(task_instance)
    test_four_b = test_four_b_task()

    test_five = BashOperator(
        task_id="test_five",
        doc_md="""unable to do that as written! Can't `import airflow`""",
        bash_command="exit 1"
    )

    test_five_b = BashOperator(
        task_id="test_five_b",
        doc_md="""We can call a separate python2.7 and pass _some_ state in via Airflow Templates and argv""",
        bash_command="""python2.7 dags/extras/py27_md5.py "{{ ti.dag_id }}" """,
        cwd="/usr/local/airflow"
    )

    test_six = PythonOperator(
        task_id="test_six",
        python_callable=test_six_fn,
        op_args=[test_four.output, test_five_b.output]
    )
