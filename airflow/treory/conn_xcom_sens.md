#### 1) Connections

В Apache Airflow **Connections (подключения)** — это способ централизованно **хранить параметры доступа** ко внешним системам и сервисам: 
базам данных, API, FTP, SSH, облачным платформам и другим источникам данных.

    
Каждое подключение содержит:

    Conn Id — уникальное имя подключения (например, my_postgres),
    
    Conn Type — тип подключения (Postgres, MySQL, HTTP, FTP, SSH, AWS и т.д.),
    

Параметры доступа:
    
    хост (host),
    
    порт (port),
    
    имя пользователя (login),
    
    пароль (password),
    
    база данных (schema),
    
    дополнительные параметры (в поле extra).     


То есть мы не прописываем логины, пароли и хосты в каждом даге, а просто используем название подключения. 

![Screenshot 2025-09-09 at 18.04.43.png](images/Screenshot%202025-09-09%20at%2018.04.43.png)

Для начала нам стоит понять, что за hook такой в коде. В Airflow hook (хук) — это объект, обеспечивающий подключение 
к внешним системам (например, к базе данных, API, хранилищу файлов и т.д.). Он инкапсулирует все детали подключения: 
логин, пароль, хост, порт, базу и методы работы с этой системой. 

`hook = PostgresHook(postgres_conn_id='pg_extra_conn')`

Airflow автоматически подставляет параметры подключения из интерфейса (Admin → Connections) по этому conn_id.

PostgresOperator (альтернатива) — это оператор в Apache Airflow, который позволяет **выполнять SQL-запросы в PostgreSQL** 
напрямую из DAG без написания Python-кода для подключения к базе.

#### 2)XCom

Как передать вычисление одной функции, которая обернута в питон оператор, другой функции, если она также обернута в питон оператор? 

Невозможно. Только если мы не будем использовать XCom. 

Возьмем простейший пример:

    from airflow import DAG
    from airflow.operators.python import PythonOperator
    from datetime import datetime
    
    # === Шаг 1: Сложение двух чисел ===
    def add_numbers(**context):
        a = 5
        b = 7
        result = a + b
        print(f"{a} + {b} = {result}")
        return result  # автоматически сохраняется в XCom
    
    # === Шаг 2: Умножение результата на другое число ===
    def multiply_result(**context):
        ti = context['ti']
        previous_result = ti.xcom_pull(task_ids='add_task')  # получаем XCom
        multiplier = 3
        final_result = previous_result * multiplier
        print(f"{previous_result} * {multiplier} = {final_result}")
    
    # === DAG ===
    with DAG(
        dag_id='xcom_math_example',
        start_date=datetime(2024, 1, 1),
        schedule_interval=None,
        catchup=False,
        description='Пример передачи данных между тасками через XCom'
    ) as dag:
    
        add_task = PythonOperator(
            task_id='add_task',
            python_callable=add_numbers,
        )
    
        multiply_task = PythonOperator(
            task_id='multiply_task',
            python_callable=multiply_result,
        )
    
        add_task >> multiply_task

Разъяснение: 

`def add_numbers(**context)`

В Python ****context** — это синтаксис для передачи всех именованных аргументов (ключей и значений) как словаря. 
В контексте Airflow **context (или **kwargs) используется для получения контекста выполнения таска.

Airflow автоматически передаёт служебный контекст (словарь с полезной информацией) в каждый PythonOperator, 
если ты принимаешь **kwargs, **context, или **_.


    ds	->              Строка с датой (execution_date в формате YYYY-MM-DD)
    ti	->              Объект TaskInstance (используется для XCom и др.)
    dag	->              Объект DAG
    task -> 	        Объект текущей задачи
    execution_date ->	Полная дата запуска DAG

Вообщем в функцию передаются какие-то параметры. За счет чего? За счет флага     
`provide_context=True`

Шаг2: Вначале функция получила контекст выполнения дага, тасок и прочей истории. Далее мы извлекли экземпляр TI. 
С помощью xcom_pull() получаем значение, которое другая задача (в данном случае — add_task) **отправила в XCom** с помощью return или xcom_push().

То есть фактически в return по некому защищенному каналу мы передали информацию, которую сможет получить только другая функция, которая укажет id таски.

`ti = context['ti']` -> Здесь ты получаешь объект TaskInstance, который содержит всё, что связано с текущей выполняемой задачей: 
её статус, время запуска, методы xcom_push и xcom_pull, и т.д.


`previous_result = ti.xcom_pull(task_ids='add_task')` -> “Дай мне результат, возвращённый задачей с task_id='add_task'”

Это сработает только если задача add_task уже завершилась, и она вернула что-то через return — Airflow сам поместил это значение в XCom.

**XCom (Cross-Communication) нужен, чтобы обмениваться данными между задачами внутри одного DAG.**

Результат первой PythonOperator-таски передать во вторую и с ним что-то сделать:

	Первая таска возвращает значение (return)
	Airflow автоматически сохраняет это значение в XCom
	Вторая таска вытаскивает это значение с помощью xcom_pull


#### 3) Sensors. 

 В Apache Airflow **сенсоры (sensors)** — это специальные операторы, которые ожидают наступления какого-либо события или состояния, 
 прежде чем пропустить выполнение следующих задач в DAG.

Существует достаточно большой список сенсоров, которые ожидают выполнение того или иного события. 
Есть параметр времени, сколько вообще ждать, есть частота проверки. То есть дежурим всю ночь, но каждый час обход. Логично? Логично.

Но вот только дежурство должно оплачиваться. Нужно место, где охрана сможет находиться, нужны ресурсы, если объект слишком большой. 
И хорошо, если это все выполняется. А если нет? Также и с сенсорами.

1. **ExternalTaskSensor**: Этот сенсор ожидает завершения определенной задачи (внешней задачи) в другом DAG. Вот пример использования ExternalTaskSensor:

        from airflow import DAG
        from airflow.operators.dummy_operator import DummyOperator
        from airflow.operators.sensors import ExternalTaskSensor
        from datetime import datetime
        
        with DAG('my_dag', schedule_interval='@daily', start_date=datetime(2023, 1, 1)) as dag:
            task1 = DummyOperator(task_id='task1')
        
            task2 = ExternalTaskSensor(task_id='wait_for_task1', external_dag_id='other_dag', external_task_id='task1')
        
            task1 >> task2

В этом примере у нас есть две задачи: task1 и wait_for_task1. Задача **wait_for_task1 является сенсором** и ожидает завершения задачи task1 в 
другом даге с идентификатором 'other_dag'. Когда task1 в другом даге завершится, wait_for_task1 продолжит выполнение.

2. FileSensor: Этот сенсор ожидает появление определенного файла на файловой системе. Вот пример использования FileSensor:

         from airflow import DAG
         from airflow.operators.sensors import FileSensor
         
         from datetime import datetime
         
         with DAG('my_dag', schedule_interval='@daily', start_date=datetime(2023, 1, 1)) as dag:
           wait_for_file = FileSensor(
               task_id='wait_for_file',
               filepath='/path/to/my/file.txt'
           )

В этом примере у нас есть задача wait_for_file, которая ожидает появление файла /path/to/my/file.txt на файловой системе. 
Когда файл будет обнаружен, задача wait_for_file продолжит выполнение.

3. HttpSensor: Этот сенсор выполняет HTTP-запрос и ожидает успешный ответ от сервера. Вот пример использования HttpSensor:

         from airflow import DAG
         from airflow.operators.sensors import HttpSensor
         
         from datetime import datetime
         
         with DAG('my_dag', schedule_interval='@daily', start_date=datetime(2023, 1, 1)) as dag:
             wait_for_api = HttpSensor(
                 task_id='wait_for_api',
                 http_conn_id='my_http_conn',
                 endpoint='/api/health'
             )

















