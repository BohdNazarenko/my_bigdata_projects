**1) PythonOperator**

_Это один из самых часто используемых операторов_. Он просто **выполняет Python-функцию**, которую Вы определили. То есть 
Вы пишите функцию, а дальше ее просто оборачиваете в обертку оператора. Это нужно для того, чтобы Airflow понял, 
что делать то нужно. **Но, стоит понять то, что весь DAG - это скрипт на Python, который может выполняться только в 
оболочке Airflow. Поэтому локально запустить DAG Вы не сможете.** 

**2) Bash Operator**

`BashOperator` в Apache Airflow — это специальный компонент, с помощью которого можно запускать команды оболочки (bash) прямо из DAG'а.
Он используется, когда нужно выполнить любую системную команду, как будто Вы вручную ввели её в терминал. Это может быть команда echo, 
запуск скрипта, копирование файлов, скачивание данных, архивирование, удаление и многое другое.
Это один из самых простых и удобных способов включить внешние действия в ваш пайплайн без написания дополнительного кода.

То есть фактически bash скрипт это возможность писать команды в терминале, по типу - 

    ls
    
    cd
    
    touch

    и многие другие команды linux.

Единственное, что важно, так это то, что bash оператор по дефолту будет смотреть в кластер, где установлен airflow. Выполним простейший даг с linux выводом.

**Dummy Operator**

Представим ситуацию, что Вы строите DAG, который сначала собирает данные, потом — обрабатывает, а потом — отправляет отчёт. 
Вы ещё не написали код для обработки, но хотите уже выстроить структуру. Тогда вы ставите `DummyOperator` вместо этой задачи. 
Он поможет проверить поток выполнения, а позже легко заменится на настоящую задачу.

Пример:

    from airflow import DAG
    from airflow.operators.empty import EmptyOperator
    from datetime import datetime
    
    default_args = {
        'owner': 'airflow',
        'start_date': datetime(2024, 1, 1),
    }
    
    dag = DAG(
        dag_id='dummy_operator_example_dag',
        default_args=default_args,
        schedule_interval=None,
        catchup=False,
        description='Пример DAG с EmptyOperator',
    )
    
    start = EmptyOperator(task_id='start', dag=dag)
    end = EmptyOperator(task_id='end', dag=dag)
    
    start >> end

![Screenshot 2025-09-08 at 18.20.07.png](images/Screenshot%202025-09-08%20at%2018.20.07.png)


#### В Airflow каждая таска — это самостоятельный шаг в вашем pipeline.

Эти шаги можно выстраивать:

**1) Последовательно**

Когда одна таска должна выполниться только после завершения другой, выстраивается цепочка зависимостей с помощью оператора >> или set_downstream()

task_1 >> task_2 >> task_3

Здесь task_2 начнёт выполняться **только после успешного выполнения** task_1, и task_3 — после task_2.


Пример:

    from airflow import DAG
    from airflow.operators.python import PythonOperator
    from datetime import datetime
    
    def step_1():
        print("Шаг 1")
    
    def step_2():
        print("Шаг 2")
    
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

![Screenshot 2025-09-08 at 18.30.57.png](images/Screenshot%202025-09-08%20at%2018.30.57.png)

Стоит обратить внимание на то, что типы тасок при любом виде выполнения могут быть любыми! 
А также по умолчанию, если таска по пути упадет с ошибкой, то остальные таски выполнены не будут.

**2) Параллельно**

Если несколько тасок не зависят друг от друга, они могут выполняться одновременно — это позволяет сократить общее время выполнения DAG'а. 
Но при это могут сильно замедлить работу системы Airflow, так как будет выделено большое количество ресурсов.

    task_1 >> [task_2, task_3]

Здесь task_2 и task_3 запустятся параллельно сразу после task_1.

Пример:

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



Получается, что здесь сначала выполнится start, а затем параллельно будут выполнены a и b. Здесь же, при падении таски start, 
также другие 2 таски выполнены не будут.

![Screenshot 2025-09-08 at 18.36.06.png](images/Screenshot%202025-09-08%20at%2018.36.06.png)

Вариант со слиянием параллельных тасок в одну

    from airflow import DAG
    from airflow.operators.python import PythonOperator
    from datetime import datetime
    
    def step_1():
        print("Начало")
    
    def parallel_a():
        print("Параллельный шаг A")
    
    def parallel_b():
        print("Параллельный шаг B")
    
    def final_step():
        print("Финальная задача после параллельных шагов")
    
    with DAG(
        'parallel_merge_dag',
        start_date=datetime(2024, 1, 1),
        schedule_interval=None,
        catchup=False,
    ) as dag:
        task1 = PythonOperator(task_id='start', python_callable=step_1)
        task2 = PythonOperator(task_id='parallel_a', python_callable=parallel_a)
        task3 = PythonOperator(task_id='parallel_b', python_callable=parallel_b)
        task4 = PythonOperator(task_id='final_step', python_callable=final_step)
    
        # Параллельные таски
        task1 >> [task2, task3]
    
        # Объединение в одну
        [task2, task3] >> task4

**3) Условно (ветвление задач)**

Airflow позволяет выполнять ветвление логики через `BranchPythonOperator`. Это означает, что на определённом этапе DAG может 
развилиться — и пойти только по одному или нескольким путям в зависимости от условий.

Пример:

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

![Screenshot 2025-09-08 at 18.47.00.png](images/Screenshot%202025-09-08%20at%2018.47.00.png)

Когда BranchPythonOperator возвращает task_id, Airflow считает, что все остальные пути были "пропущены" (skipped). 
А если у DummyOperator end есть несколько родителей , и хотя бы один из них был skipped, то по умолчанию и end тоже не выполняется, 
потому что он зависит от всех своих upstream-задач. Поэтому начинаем понимать, что у каждой таски есть 2 очень важных параметра - 

    а) Правило ее выполнения (Trigger rule)
    
    б) Статус, которые влияет на этот самый Trigger Rule

В Apache Airflow у задач (тасок) есть основные статусы (состояния выполнения), которые позволяют понять, что происходит 
с каждой задачей в процессе работы DAG’а. Ниже приведены основные статусы, как они появляются, и в каких случаях используются.

**1) Зелёный — success**

«Я всё сделал, задание выполнено!»

![Screenshot 2025-09-08 at 18.49.54.png](images/Screenshot%202025-09-08%20at%2018.49.54.png)

**2) Красный — failed**

«Ой, что-то пошло не так…»

![Screenshot 2025-09-08 at 18.50.41.png](images/Screenshot%202025-09-08%20at%2018.50.41.png)

**3) Светло-зеленый — running**

«Не трогайте меня, я сейчас работаю!»

![Screenshot 2025-09-08 at 18.51.14.png](images/Screenshot%202025-09-08%20at%2018.51.14.png)

**4) Желтый — up_for_retry**

«Не получилось, но я не сдаюсь — попробую ещё!»
Если задача упала, но вы предусмотрительно дали ей шанс (retries > 0), она немного отдохнёт (retry_delay) и попробует снова. Пока она в ожидании — она желтая.

![Screenshot 2025-09-08 at 18.52.06.png](images/Screenshot%202025-09-08%20at%2018.52.06.png)

**5) Серый — queued**

«Я в очереди, скоро начну.»
Когда Scheduler решил, что задача должна выполниться, но она пока не назначена Executor'у, она находится в очереди. Значит, пока нет ресурсов и нужно подождать.

![Screenshot 2025-09-08 at 18.53.05.png](images/Screenshot%202025-09-08%20at%2018.53.05.png)

**6) Белый — none или «без статуса»**

«Я ещё ни разу не запускался.»

![Screenshot 2025-09-08 at 18.54.05.png](images/Screenshot%202025-09-08%20at%2018.54.05.png)

**7) Розовый — skipped**

«Это не моя очередь, пропускаю.»
Иногда задачи вообще не должны запускаться. Например, если был выбор между четный день и нечетный, а задача оказалась 
не на том пути. Такие задачи Airflow помечает как skipped и подсвечивает розовым.

![Screenshot 2025-09-08 at 18.54.59.png](images/Screenshot%202025-09-08%20at%2018.54.59.png)

В зависимости от версии Airflow цвет может меняться, но статусы уже 100 лет как остаются с одними и теми же названиями.

