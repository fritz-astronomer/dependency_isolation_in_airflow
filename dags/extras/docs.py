doc = """
## Fitness Test
1) Run a SQL Operator with an Airflow Connection, return results as an XCOM, and use an Airflow Template in the SQL
2) Do #1 with an older version of the `PostgresOperator` than the one installed in the parent `requirements.txt`
3) Run `ruby` with an and Airflow Template and return results as an XCOM
4) Run a Python function that consumes an Airflow Template and is written alongside the DAG, importing a function in the `/include` folder. Return the results as an XCOM
5) Do #4 in python2.7
6) Combine the #4 + #5 via consuming an XCOM and print if they match

"""