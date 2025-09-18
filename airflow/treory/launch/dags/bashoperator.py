from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
}

dag = DAG(
    dag_id='simple_bash_operator_dag',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    description='Простой DAG с BashOperator',
)

bash_task = BashOperator(
    task_id='print_hello',
    bash_command='echo "Привет из Bash!"',
    dag=dag,
)

bash_task