from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime

# Вычисления вне операторов
result = sum(range(1000))  # <-- Выполнится при импорте DAG

def my_task():
    print(f"Результат вычислений: {result}")

dag = DAG(
    dag_id='precalculated_result_dag',
    default_args={'start_date': datetime(2024, 1, 1)},
    schedule_interval=None,
    catchup=False,
)

task = PythonOperator(
    task_id='print_result',
    python_callable=my_task,
    dag=dag,
)