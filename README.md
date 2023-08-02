# Dependency Isolation in Airflow


## Fitness Tests

1) Run a SQL Operator with an Airflow Connection, return results as an XCOM, and use an Airflow Template in the SQL
2) Do #1 with an older version of the `PostgresOperator` than the one installed in the parent `requirements.txt`
3) Run `ruby` with an and Airflow Template and return results as an XCOM
4) Run a Python function that consumes an Airflow Template and is written alongside the DAG, importing a function in the `/include` folder. Return the results as an XCOM
5) Do #4 in python2.7
6) Combine the #4 + #5 via consuming an XCOM and print if they match

### Restrictions for tests
- Cannot use volumes or complex knowledge of underlying implementation (e.g. kubernetes)
- Test fails if the "solution" is effectively recreating one of the other solutions in a worse/more complex way

### Results

| Test             | #1   | #2    | #3  | #4   | #5    | #6  |
|------------------|------|-------|-----|------|-------|-----|
| Vanilla          | ✔️   | ❌     | ✔️  | ✔️   | ❌,✔️️ | ✔️  |
| EPO              | 🔎️  | ✔️,⚠️ | 🔎  | ✔️   | ⚠️    | 🔎  |
| KPO              | ❌,✔️ | ❌     | ✔️  | ❌,️❌ | ❌     | ❌   |
| IsolatedOperator | 🔎   | ✔️ ⏳  | 🔎  | ⚠️⏳  | ⚠️⏳   | 🔎  |

#### Labels

| Icon | Meaning                  |
|------|--------------------------|
| 🔎️  | Refer to Vanilla Impl    |
| ✔️   | Works                    |
| ❌    | Cannot work              |
| ⚠️   | Works with caveats       |
| ⏳    | Can work with dev effort |


## Setup Steps

1) **Init project** `astro dev init`
2) (optional) `python -m venv venv && echo "venv" >> .gitignore`
    - I do this so pycharm has an interpreter to use

   [//]: # (3&#41; `astro registry provider add amazon` - adds the [Amazon provider]&#40;https://registry.astronomer.io/providers/apache-airflow-providers-amazon/versions/8.3.1/&#41;)
3) **[Postgres provider](https://registry.astronomer.io/providers/apache-airflow-providers-postgres)**
    1) add via `astro registry provider add postgresql`
    2) add to `.env`: `AIRFLOW_CONN_PSQL="postgresql://postgres:postgres@postgres:5432"`
4) **[Kubernetes provider](https://registry.astronomer.io/providers/apache-airflow-providers-cncf-kubernetes)**
    1) these instructions are assuming you are already locally running and have set up Minikube, Docker Desktop with
       Kubernetes, microk8s, k3s, etc. You can run `kubectl get namespaces`
    2) add via `astro registry provider add kubernetes`
    2) Add to `.env`:
        ```shell
        KC=$(python -c "import sys, urllib.parse, yaml; print(urllib.parse.quote(yaml.dump(yaml.safe_load(open(sys.argv[1]))).replace('127.0.0.1', 'host.docker.internal')))" ~/.kube/config)
        echo "AIRFLOW_CONN_KUBERNETES='kubernetes://?extra__kubernetes__namespace=default&extra__kubernetes__kube_config=$KC'"
        ```
5) **ExternalPythonOperator** - [use the (optional) helper here](https://github.com/astronomer/astro-provider-venv/)
    1) Add `astro-provider-venv` to the **parent** `requirements.txt`
    2) Prepend `# syntax=quay.io/astronomer/airflow-extensions:v1` to your `Dockerfile`
    3) Append `PYENV 3.10 data-science environments/data-science/requirements.txt`
    4) Add `apache-airflow-providers-postgres==3.0.0` to the child's `requirements.txt` (an old version of the Postgres
       Provider)
    5) Add `gcc` and `python3-dev` to the **parent's** `packages.txt` (just needed for the Postgres Provider)
6) (optional) `source venv/bin/activate && pip install -r requirements.txt`
    - just to keep pycharm up-to-date
7) **ruby**
    1) Add `ruby` to `packages.txt`
8) **python2.7**
    1) Add `python2.7` to `packages.txt`
    2) Add `__init__.py` to `include`
9) **IsolatedOperator**
    1) Add the following to your **child** `Dockerfile`
        ```
        # Install system-level packages
        COPY packages.txt .
        USER root
        RUN if [[ -s packages.txt ]]; then \
            apt-get update && cat packages.txt | tr '\r\n' '\n' | sed -e 's/#.*//' | xargs apt-get install -y --no-install-recommends \
            && apt-get clean \
            && rm -rf /var/lib/apt/lists/*; \
          fi
 
        # Install python packages
        COPY requirements.txt .
        RUN if grep -Eqx 'apache-airflow\s*[=~>]{1,2}.*' requirements.txt; then \
            echo >&2 "Do not upgrade by specifying 'apache-airflow' in your requirements.txt, change the base image instead!";  exit 1; \
          fi; \
          pip install --no-cache-dir --root-user-action=ignore -r requirements.txt
        USER astro
       ```
    2) run a docker registry locally `docker run -d -p 5000:5000 --restart=always --name registry registry:2`
    3) Build and push **parent** Docker image (with `astro` cli) and **children** images (with docker directly) via `sh build_all.sh -r localhost:5000`
10) **Start the project** `astro dev start` 
