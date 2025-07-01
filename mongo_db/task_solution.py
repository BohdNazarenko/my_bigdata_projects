import json
import os

from mongo_db.mongo_data_insert import db
from datetime import datetime, timedelta

#Collections for users active and archive
archived_col = db["archived_users"]
events_col = db["user_events"]


#Time constants
now = datetime.now()
register_day = now - timedelta(days=30)
active_day = now - timedelta(days=14)

#Pipeline for filter users
pipeline = [
    {
        "$group": {
            "_id": "$user_id",
            "registration_date": {"$first": "$user_info.registration_date"},
            "event_time": {"$max": "$event_time"},
        }
    },
        {
        "$match" : {
            "registration_date" : {"$lt": register_day},
            "event_time" : {"$lt": active_day},
        }
    }
]


#query to mongodb to aggregate data which return list of qualified users
users = list(events_col.aggregate(pipeline))

#Extract user IDs
user_ids = [user["_id"] for user in users]

#Copy documents into the archive collection
for doc in events_col.find({"user_id": {"$in": user_ids}}):
    archived_col.replace_one({"_id": doc["_id"]}, doc, upsert=True)

#Json report build
json_report = {
    "date" : now.strftime("%Y-%m-%d"),
    "archived_users_count" : len(user_ids),
    "archived_user_ids": user_ids
}

#create filename with current day name and json format
os.makedirs("reports", exist_ok=True)
filename = f"{now:%Y-%m-%d}.json"

with open(filename, "w") as f:
    json.dump(json_report, f, ensure_ascii=False, indent=4)

#my tests to check id_s length
print("user_events :", events_col.estimated_document_count())
print("archived_users :", archived_col.estimated_document_count())
