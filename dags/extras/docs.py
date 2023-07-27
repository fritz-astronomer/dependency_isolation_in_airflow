doc = """
# Fitness Test
1) Run a sql operator with a connection w/ a xcom + template
    - SQLExecuteQueryOperator(sql="SELECT 1;", conn_id="...")
2) do it with an older version of the `PostgresOperator` 
3) Run a bash operator with ruby, w/ a xcom + template
    - BashOperator(bash_command=\"\"\"ruby -e 'puts "Hello world \{\{\}\}"'\"\"\")
4) Run a python operator, invoking a fn in the dag that imports a fn in the include folder, w/ a xcom + template
5) Do it #4 in python2.7
6) Combine the #4 + #5 via xcom and print if they match
"""