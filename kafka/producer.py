from datetime import datetime

from dateutil.relativedelta import relativedelta
from kafka import KafkaProducer
import json
import time
import random

import psycopg2

#create producer
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

#Connect to db
conn = psycopg2.connect(
    dbname="test_db", user="admin", password="admin", host="localhost", port=5432
)
cursor = conn.cursor()


cursor.execute("""
--create user_logins table
CREATE TABLE IF NOT EXISTS user_logins (
    id SERIAL         PRIMARY KEY,
    login             VARCHAR(25),
    balance           NUMERIC(9, 2),
    registration_time TIMESTAMP,
    purchase_date     TIMESTAMP
);
    
--table for sending to consumer status    
CREATE TABLE IF NOT EXISTS user_logins_kafka_status
(
    id INT PRIMARY KEY REFERENCES user_logins(id) ON DELETE CASCADE,
    sent_to_kafka BOOLEAN NOT NULL DEFAULT FALSE
);    
    
--function for inserting new ids on user_logins_kafka_status from user_logins by trigger
CREATE OR REPLACE FUNCTION logins_inserter()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO user_logins_kafka_status(id) 
    VALUES (NEW.id)
    ON CONFLICT DO NOTHING;
    RETURN NEW;
END;
$$;

--trigger for logins_inserter() function
CREATE OR REPLACE TRIGGER trg_log_ins
AFTER INSERT ON user_logins
FOR EACH ROW
EXECUTE FUNCTION logins_inserter();
""")
conn.commit()


#Sample users
users = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
    "William", "Elizabeth", "David", "Barbara", "Joseph", "Susan", "Thomas", "Jessica",
    "Charles", "Sarah", "Christopher", "Karen", "Daniel", "Nancy", "Matthew", "Lisa",
    "Anthony", "Margaret", "Mark", "Betty", "Donald", "Sandra", "Steven", "Ashley",
    "Paul", "Kimberly", "Andrew", "Donna", "Joshua", "Emily", "Kenneth", "Carol",
    "Kevin", "Michelle", "Brian", "Amanda", "George", "Dorothy", "Timothy", "Melissa",
    "Ronald", "Deborah", "Edward", "Stephanie", "Jason", "Rebecca", "Jeffrey", "Laura",
    "Ryan", "Sharon", "Jacob", "Cynthia", "Gary", "Kathleen", "Nicholas", "Amy",
    "Eric", "Shirley", "Jonathan", "Angela", "Stephen", "Helen", "Larry", "Anna",
    "Justin", "Brenda", "Scott", "Pamela", "Brandon", "Nicole", "Benjamin", "Ruth",
    "Samuel", "Katherine", "Gregory", "Samantha", "Frank", "Christine", "Alexander",
    "Catherine", "Raymond", "Virginia", "Patrick", "Rachel", "Jack", "Carolyn",
    "Dennis", "Janet", "Jerry", "Maria", "Tyler", "Julie"
]

data = {}


#Data pipeline generate records
for i in range(0, 20):
    data = {
        "login": random.choice(users),
        "balance": round(random.uniform(0, 10_000), 2),
        "registration_time": (datetime.now() - relativedelta(months=6)).timestamp(),    #sample simple registration date
        "purchase_date": time.time()
    }

    #Insert records into pg
    print("Received:", data)
    cursor.execute(
        "INSERT INTO user_logins (login, balance, registration_time, purchase_date) "
        "VALUES (%s, %s, to_timestamp(%s), to_timestamp(%s))",
        (data["login"], data["balance"], data["registration_time"], data["purchase_date"])
    )

    conn.commit()


#extract data from db to list of tuples and filter only for new logins
cursor.execute("""
               SELECT ul.id,
                      ul.login,
                      ul.balance, 
                      extract(epoch FROM ul.registration_time),
                      extract(epoch FROM ul.purchase_date)
                FROM user_logins AS ul
                LEFT JOIN user_logins_kafka_status AS ks
                        ON ks.id = ul.id
                WHERE ks.sent_to_kafka IS FALSE
                ORDER BY ul.id
               """)
rows = cursor.fetchall()


#insert data from list of tuples of new actions to producer
for row in rows:
    row_id = row[0]

    data = {
        "login": row[1],
        "balance": float(row[2]),
        "registration_time": float(row[3]),
        "purchase_date": float(row[4])
    }

    producer.send("migration_db", value=data)
    print("Sent:", data)

    time.sleep(0.5)

    cursor.execute("""
        UPDATE user_logins_kafka_status
        SET sent_to_kafka = TRUE
        WHERE id = %s
    """,
    (row_id, )
    )

conn.commit()




