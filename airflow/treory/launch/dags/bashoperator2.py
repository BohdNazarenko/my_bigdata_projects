from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime


default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
}

dag = DAG(
    dag_id='list_directories_dag',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    description='DAG, который выводит список директорий',
)
list_dirs_task = BashOperator(
    task_id='list_directories',
    bash_command='ls -la',  # Показать подробный список файлов и папок
    dag=dag,
)


list_dirs_task