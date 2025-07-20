#
# consumer = KafkaConsumer(
#     'test-topic',                                                                 #name or name list for consumer
#     bootstrap_servers=['localhost:9092'],                                         #entrypoint for kafka cluster
#     auto_offset_reset='earliest',                                                 #from beginning of partition (latest -> only new messages)
#     enable_auto_commit=True,                                                      #client auto commit 5000 mc
#     group_id='test-group',                                                        #consumer group name
#     value_deserializer=lambda value: json.loads(value.decode('utf-8')),           #bite -> UTF-8 -> dict (object Python)
# )
#
# print("Waiting for messages...")
# for message in consumer:
#     print(f"Received message: {message.value}")                                   #
from kafka import KafkaConsumer
import json
import clickhouse_connect

consumer = KafkaConsumer(
    "user_events",
    bootstrap_servers="localhost:9092",
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

client = clickhouse_connect.get_client(host='localhost', port=8123, username='user', password='strongpassword')

client.command("""
CREATE TABLE IF NOT EXISTS user_logins (
    username String,
    event_type String,
    event_time DateTime
) ENGINE = MergeTree()
ORDER BY event_time
""")

for message in consumer:
    data = message.value
    print("Received:", data)
    client.command(
        f"INSERT INTO user_logins (username, event_type, event_time) VALUES ('{data['user']}', '{data['event']}', toDateTime({data['timestamp']}))"
    )
