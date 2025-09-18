from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def step_1():
    print("Начало")

def parallel_a():
    print("Параллельный шаг A")

def parallel_b():
    print("Параллельный шаг B")

with DAG(
    'parallel_dag',
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
) as dag:
    task1 = PythonOperator(task_id='start', python_callable=step_1)
    task2 = PythonOperator(task_id='parallel_a', python_callable=parallel_a)
    task3 = PythonOperator(task_id='parallel_b', python_callable=parallel_b)

    task1 >> [task2, task3]