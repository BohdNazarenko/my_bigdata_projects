Добрый день!

Я немного решил заморочиться над заданием, и какое правильное, с точки зрение производительности и 
лаконичности кода есть решение я не знаю, вторую часть вебинара я еще не смотрел :)

В директории проекта есть директория [`kafka`](kafka), в которой лежат:

1) [`docker-compose.yml`](kafka/first_study_pipeline/docker-compose.yml) - 
который запускается c помощью терминала командой `docker-compose up -d`, находясь в директории папки [`kafka`](kafka) 
с открытым Docker Desktop на компьютере (знаю что вы лучше меня это знаете, но хочется научиться писать ридми 
максимально понятно даже тому, кто ни разу не программировал😊);


2) [`producer.py`](kafka/first_study_pipeline/producer.py) - который запускается с помощью терминала командой `python 
producer.py` находясь в директории kafka проекта.

В данном модуле создается объект-клиент KafkaProducer, который запускает фоновый поток, bootstrap_servers с подключением
к дефолтному порту 9092 и value_serializer, который превращает объект пайтона в JSON-строку с кодировкой UTF-8, чтобы 
producer превратил его в байтовый массив.

Я решил не менять схему таблицы, а вместо этого создать новую user_logins_kafka_status с колонками 
id(связь один к одному с id таблицы user_logins) и sent_to_kafka boolean (статус отправки записи в producer). 
Я это автоматизировал с помощью Trigger, очень удобно, что он сам по мере поступления новых полей добавляет его id в 
таблицу user_logins_kafka_status.

Далее я создал тестовых юзеров, сгенерировал их записи и добавил их в таблицу user_logins. Далее с помощью курсора и
Left join я выбрал только записи со статусом False и добавил их в качестве листа словарей в локальную переменную rows. Далее 
из переменной rows данные берутся единично с помощью цикла и отправляются в producer. И лишь потом в таблице user_logins_kafka_status
меняется статус записи из FALSE на TRUE. 

3) [`consumer.py`](kafka/first_study_pipeline/consumer.py) запускается командой `python consumer.py` находясь в 
директории kafka проекта. Здесь я изменил только схему таблицы для миграции, а остальной код взят из примера "5.1 Введение в streaming 3 страница". 

Проект работает, можно это протестировать с уже включенными producer и consumer sql командами:

Postgres:

1) SELECT * FROM user_logins; - для просмотра всех записей таблицы user_logins,


2) SELECT COUNT(*) FROM user_logins; - для просмотра кол-ва записей таблицы user_logins,


3) SELECT * FROM user_logins_kafka_status; - для просмотра всех записей таблицы user_logins_kafka_status,


4) SELECT COUNT(*) FROM user_logins_kafka_status; - для просмотра кол-ва записей таблицы user_logins_kafka_status,

5) BEGIN;
TRUNCATE user_logins_kafka_status,
         user_logins;
COMMIT;   - удобный способ удаления данных из таблиц user_logins_kafka_status и user_logins_kafka_status связанных между
собой каскадно.

Clickhouse:

1) SELECT COUNT(*) FROM user_logins; - для просмотра всех записей таблицы user_logins (после запущенных producer и consumer)
количество записей должны совпадать;


2) SELECT COUNT(distinct *) FROM user_logins; - для просмотра кол-ва уникальных записей таблицы user_logins (число должно 
совпадать с COUNT(*));


3) TRUNCATE TABLE user_logins; - очистка записей таблицы user_logins.


Спасибо за внимание 🤗

