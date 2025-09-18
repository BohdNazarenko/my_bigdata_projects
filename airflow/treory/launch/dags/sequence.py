from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def step_1():
    print("Шаг 1")

def step_2():
    print("Шаг 228")

def step_3():
    print("Шаг 3")

with DAG(
    'sequential_dag',
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
) as dag:
    task1 = PythonOperator(task_id='step_1', python_callable=step_1)
    task2 = PythonOperator(task_id='step_2', python_callable=step_2)
    task3 = PythonOperator(task_id='step_3', python_callable=step_3)

    task1 >> task2 >> task3








