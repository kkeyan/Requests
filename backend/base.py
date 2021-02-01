from flask import Flask, make_response, request
import json, requests
from db import DataBase as db
app = Flask(__name__)
import datetime
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()


def request_processor(status, data):
    return make_response({'status': status, 'data': data})


def add_job(task):
    task_id = str(task['id'])
    interval_seconds = task['request_interval_seconds']
    if scheduler.get_job(task_id):
        print('rescheduling the existing job')
        scheduler.remove_job(task_id)
    print('Adding the job')
    scheduler.add_job(execute_job,
                          'interval', [task],
                          seconds=interval_seconds,
                          id=task_id)


def write_to_tasks(status, task):
    database = db()
    sql = f"Insert into tasks (task_name, task_id, task_status, task_last_run) values('{task['name']}',{task['id']},'{status}', '{datetime.datetime.now()}');"
    database.execute_query(sql)
    dformat = "%d-%m-%y %H:%M:%S"
    sql = f"update requests set status = '{status} on {datetime.datetime.now().strftime(dformat)}' where id = {task['id']};"
    database.execute_query(sql)
    return True


def execute_job(task):
    request_url = json.loads(task['request'])['url']
    if not task['is_active']:
        write_to_tasks('Is inactive', task)
        return
    task_res = requests.get(request_url)
    if task_res.status_code == 200:
        write_to_tasks('Sucess', task)
    else:
        write_to_tasks('Failure', task)
    return


@app.route('/')
def proj_root():
    return request_processor(True, [])


@app.route('/users', methods=['GET', 'POST'])
def get_users():
    if request.method == 'GET':
        return request_processor(True, db().get_data_from_table('users') or [])
    else:
        data = request.get('data')
        return request_processor(True,
                                 db().put_data_into_table('users', data) or [])


@app.route('/requests', methods=['GET', 'POST'])
def get_requests():
    if request.method == 'GET':
        results = db().get_data_from_table('requests')
        if results:
            for i in results:
                i['notifications'] = json.loads(i['notifications'])
                i['request'] = json.loads(i['request'])
        return request_processor(True, results or [])
    else:
        data = request.json
        data['notifications'] = json.dumps(data['notifications'])
        data['request'] = json.dumps(data['request'])
        response = db().put_data_into_table('requests', data) or []
        add_job(data)
        return request_processor(True, response)


@app.route('/tasks')
def get_tasks():
    db_new = db()
    return request_processor(True, db_new.get_data_from_table('tasks'))


@app.route('/data', methods=['POST'])
def get_data_from_url():
    data = request.json
    url = data['url']
    return request_processor(True, requests.get(url).content.decode('utf-8'))


@app.route('/requests/<action>', methods=['POST'])
def perform_request_action(action):
    db_new = db()
    data = request.json
    if action == 'pause':
        sql = f"""update requests set is_active = 0, status = 'Inactive', updated = '{datetime.datetime.now()}' where id = {data['id']};"""
        scheduler.pause_job(str(data['id']))
    elif action == 'resume':
        sql = f"""update requests set is_active = 1, status = 'Active', updated = '{datetime.datetime.now()}' where id = {data['id']};"""
        scheduler.resume_job(str(data['id']))
    elif action == 'delete':
        sql = f"""delete from requests where id = {data['id']};"""
        scheduler.resume_job(str(data['id']))
    return request_processor(True, db_new.execute_query(sql))


if __name__ == '__main__':
    database = db()
    database.setup_db()
    scheduler.start()
    request_check = "select * from requests;"
    for request_json in database.execute_query(request_check):
        add_job(request_json)
    app.run(debug=True)
