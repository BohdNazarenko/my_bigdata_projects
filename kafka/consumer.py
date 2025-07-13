# consumer_to_clickhouse.py
from kafka import KafkaConsumer
import json
import clickhouse_connect

consumer = KafkaConsumer(
    "migration_db",
    bootstrap_servers="localhost:9092",
    # group_id="user-logins-consumer",
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

client = clickhouse_connect.get_client(host='localhost', port=8123, username='user', password='strongpassword')

client.command("""
CREATE TABLE IF NOT EXISTS user_logins (
    login             String,
    balance           Decimal(9, 2),      
    registration_time DateTime,
    purchase_date     DateTime
    
) ENGINE = MergeTree()
ORDER BY registration_time
""")


for message in consumer:
    data = message.value
    print("Received:", data)
    client.command(
        f"INSERT INTO user_logins (login, balance, registration_time, purchase_date)"
        f" VALUES ('{data['login']}', '{data['balance']}', toDateTime({data['registration_time']}), toDateTime({data['purchase_date']}))"
    )
