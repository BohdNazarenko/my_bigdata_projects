# BigData Journey — Airflow SQL Runner

Mini‑project: Airflow runs all .sql files from the folder every day at 09:00 and writes metrics to the dm.* marts.

Analysts put their scripts into sources/ — the DAG picks them up automatically.

## What’s inside

	•	Airflow (webserver, scheduler, worker) + CeleryExecutor
	•	Redis — task broker
	•	Postgres (postgres) — Airflow metadata DB
	•	Postgres (pg_shop) — working shop database (data/marts)
	•	DAG daily_sql_runner — reads SQL from sources/ and runs them in alphabetical order every day at 09:00

Requirements

	•	Docker + Docker Compose
	•	Free ports: 8080 (Airflow UI), 5433 (pg_shop exposed)

Project structure

    project-root/
    ├─ docker-compose.yml
    ├─ dags/
    │  ├─ daily_sql_runner.py      # DAG: runs *.sql from sources/
    │  └─ hello_world.py           # demo DAG (optional)
    ├─ sources/                    # analysts put daily .sql here
    │  ├─ 01_customer_behavior_analise.sql
    │  └─ 02_sales_analise.sql
    ├─ sql_initialise_scripts/     # one-time DB initialization scripts
    │  ├─ create_db.sql
    │  ├─ create_tables.sql
    │  └─ initial_db.sql
    ├─ plugins/                    # (optional) custom Airflow plugins
    └─ logs/                       # Airflow logs (mounted in the container)

In docker-compose.yml the local ./sources folder is mounted into the container as /opt/airflow/sources, and the DAG reads the path from the env var SQL_DIR=/opt/airflow/sources.

How to run:

### 1.	Build the image

`docker build -t airflow-with-java .`

### 2.	Start the stack

`docker-compose up --build`

### 3.	Open Airflow UI: 

http://localhost:8080  

Default login/password: airflow / airflow.

### 4.	Create a Connection to the shop DB (if it isn’t there yet):

UI → Admin → Connections → +

	•	Conn Id: shop_pg
	•	Conn Type: Postgres
	•	Host: pg_shop
	•	Port: 5432
	•	Schema/Database: shop_analytics (or retail if that’s where your data is)
	•	Login: shop_user
	•	Password: shop_password

### 5.	Trigger the DAG manually (UI: Trigger DAG) to test.

How daily_sql_runner works

	•	Takes the SQL path from SQL_DIR (default /opt/airflow/sources).
	•	Collects all *.sql, sorts by filename (01_*.sql, 02_*.sql, …).
	•	Passes the filename to an operator; the operator reads the file from template_searchpath and renders Jinja variables (e.g., {{ ds }}).
	•	Executes sequentially. A short summary is written to the log at the end.

Where to put SQL and how to name it

    •	Put files into sources/ and prefix them to control order, for example:
	•	01_customer_behavior_analise.sql
	•	02_sales_analise.sql

## Where to see results

### 1. In the Airflow UI


	•	DAGs → daily_sql_runner → Grid/Graph — task statuses.
	•	Click a task → Log (executed SQL), Rendered (how {{ ds }} was substituted).

### In the database

`SELECT * FROM dm.daily_customer_metrics ORDER BY d DESC;`
`SELECT * FROM dm.daily_sales_totals  ORDER BY d DESC;`