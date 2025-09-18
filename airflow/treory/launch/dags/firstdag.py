from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.trigger_rule import TriggerRule
from datetime import datetime

def success_task():
    print("Успешная задача")

def failed_task():
    raise Exception("Задача упала")

def always_task():
    print("Эта задача выполняется независимо от статуса предыдущих")

with DAG(
    'trigger_rule_demo',
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False
) as dag:

    task_ok = PythonOperator(
        task_id='success_task',
        python_callable=success_task
    )

    task_fail = PythonOperator(
        task_id='fail_task',
        python_callable=failed_task
    )

    final_task = PythonOperator(
        task_id='always_run',
        python_callable=always_task,
        trigger_rule=TriggerRule.ALL_DONE  # Выполнится, даже если предшественники упали
    )

    [task_ok, task_fail] >> final_task