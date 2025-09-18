from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.dummy import DummyOperator
from datetime import datetime

def choose_path():
    import datetime
    if datetime.datetime.now().day % 2 == 0:
        return 'even_day'
    else:
        return 'odd_day'

def even_task():
    print("Сегодня чётный день")

def odd_task():
    print("Сегодня нечётный день")

with DAG(
    'branching_dag',
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
) as dag:
    branch = BranchPythonOperator(
        task_id='branch_logic',
        python_callable=choose_path
    )

    even = PythonOperator(task_id='even_day', python_callable=even_task)
    odd = PythonOperator(task_id='odd_day', python_callable=odd_task)

    end = DummyOperator(task_id='end')

    branch >> [even, odd]
    even >> end
    odd >> end