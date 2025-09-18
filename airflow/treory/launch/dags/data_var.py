from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from datetime import datetime

def print_data_path():
    path = Variable.get("data_dir")
    print(f"Путь к данным: {path}")

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
}

with DAG(
    dag_id='example_variable_usage',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    description='Пример использования переменной в Airflow DAG',
) as dag:

    show_path = PythonOperator(
        task_id='show_data_dir',
        python_callable=print_data_path,
    )

    show_path