import requests, json
from db import DataBase
import datetime
urlrequests = "https://vendorshtml.s3.us-east-2.amazonaws.com/requests.json"
urlusers = "https://vendorshtml.s3.us-east-2.amazonaws.com/users.json"
jobsColumn = """(`id`, `status`, `name`, `created_by`, `notifications`, `timezone`, `request`, `request_interval_seconds`, `tolerated_failures`, `created`, `updated`)"""
usersColumn = """(`id`, `photoUrl`, `name`, `label`, `type`)"""

def initial_upload():
    db = DataBase()
    all_requests = json.loads(requests.get(urlrequests).content)
    all_users = json.loads(requests.get(urlusers).content)
    all_users = all_users['data']
    # print(all_requests)
    for r in all_requests:
        insertSt = f"insert into requests {jobsColumn} values({r['id']}, '{r['status']}', '{r['name']}',99, '{json.dumps(r['notifications'])}', '{r['timezone']}','{json.dumps(r['request'])}','{r['request_interval_seconds']}','{r['tolerated_failures'] or 5}','{r['created']}', '{datetime.datetime.now()}');"
        db.execute_query(insertSt)
    for user in all_users:
        insertSt = f"insert into users {usersColumn} values ({user['id']}, '{user['photoUrl']}', '{user['name']}', '{user['label']}', '{user['type']}');"
        db.execute_query(insertSt)
    # print(all_users)
initial_upload()
