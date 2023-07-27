import os
from datetime import datetime

from airflow import DAG
from airflow.decorators import task
from airflow.operators.python import PythonOperator, ExternalPythonOperator

from dags.extras import docs
from dags.extras.epo_fn import old_postgres
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


with DAG("epo_2", schedule=None, start_date=datetime(1970, 1, 1), doc_md=docs.doc):
    test_two = ExternalPythonOperator(
        task_id='test_two',
        doc_md="""
        Note: We needed to install System Dependencies in the parent packages.txt.
        
        The function must be defined using def, and not be part of a class. 
        
        All imports must happen inside the function and no variables outside the scope may be referenced. 
        
        A global scope variable named virtualenv_string_args will be available (populated by string_args). 

        In addition, one can pass stuff through op_args and op_kwargs, and one can use a return value. 
        
        Note that if your virtualenv runs in a different Python major version than Airflow, you cannot use return 
        values, op_args, op_kwargs, or use any macros that are being provided to Airflow through plugins. 
        You can use string_args though.
        
        If Airflow is installed in the external environment in different version that the version used by 
        the operator, the operator will fail.,
        """,
        python_callable=old_postgres,
        python=os.environ["ASTRO_PYENV_data-science"],
        templates_dict={"my_dag_id": "{{ ti.dag_id }}"}
    )

    @task.venv(
        "data-science",
        doc_md="""Just to show off taskflow style with https://github.com/astronomer/astro-provider-venv
        NOTE: This didn't get correctly interpolated - so **partial failure**""",
        templates_dict={"my_dag_id": "{{ ti.dag_id }}"}
    )
    def task_two_b(templates_dict=None):
        from dags.extras.epo_fn import old_postgres
        return old_postgres(templates_dict=templates_dict)
    task_two_b()

    test_four = PythonOperator(
        task_id="test_four",
        doc_md="""Same as vanilla""",
        python_callable=test_four_fn
    )

    def run_py27_md5():
        """Couldn't call it directly as that'd interfere with the DAG being parsed"""
        from dags.extras import py27_md5
        global virtualenv_string_args
        return py27_md5.main(virtualenv_string_args[0])

    test_five = ExternalPythonOperator(
        task_id="test_five",
        doc_md="""We can call py2.7 via the EPO, but we can't get airflow context templates :/ so partial failure""",
        python="/usr/bin/python2.7",
        python_callable=run_py27_md5,
        string_args=["{{ ti.dag_id }}"],
        expect_airflow=False,
    )

    test_six = PythonOperator(
        task_id="test_six",
        python_callable=test_six_fn,
        op_args=[test_four.output, test_five.output]
    )
