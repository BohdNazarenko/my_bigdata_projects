Основные trugger rule для тасок

![Screenshot 2025-09-08 at 18.56.41.png](images/Screenshot%202025-09-08%20at%2018.56.41.png)

Используем в коде:

    from airflow import DAG
    from airflow.operators.python import PythonOperator, BranchPythonOperator
    from airflow.operators.dummy import DummyOperator
    from airflow.utils.trigger_rule import TriggerRule
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
            python_callable=choose_path         <--- условие
        )
    
        even = PythonOperator(task_id='even_day', python_callable=even_task)
        odd = PythonOperator(task_id='odd_day', python_callable=odd_task)
    
        end = DummyOperator(
            task_id='end',
            trigger_rule=TriggerRule.ONE_SUCCESS  # <-- ключевая строка
        )
    
        branch >> [even, odd]
        even >> end
        odd >> end

![Screenshot 2025-09-08 at 19.04.31.png](images/Screenshot%202025-09-08%20at%2019.04.31.png)

Переменные в Apache Airflow — это глобальные ключ-значение параметры, которые можно использовать в DAG'ах и задачах для настройки поведения, 
не изменяя код. Они особенно полезны для хранения:

    путей к файлам,
    
    URL API,
    
    токенов (если нет строгих требований к безопасности),
    
    параметров конфигурации DAG'ов,
    
    флагов включения/отключения логики.

















