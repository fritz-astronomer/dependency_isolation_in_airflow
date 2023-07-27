
def old_postgres(**context):
    import sys
    from airflow.providers.postgres.operators.postgres import PostgresOperator
    from airflow.providers_manager import ProvidersManager

    print(f"My python version is {sys.version}")

    for key, provider in ProvidersManager().providers.items():
        if key == 'apache-airflow-providers-postgres':
            print(f"My postgres provider version is {provider.version}")

    return PostgresOperator(
        task_id="ISOLATED_TASK",
        sql=f"""SELECT 1, '{context.get('templates_dict', {}).get("my_dag_id", "")}';""",
        postgres_conn_id="PSQL"
    ).execute({})