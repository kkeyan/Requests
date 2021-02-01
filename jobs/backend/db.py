import mysql.connector as mysql
from config import Config
import datetime
from dateutil import parser as date_parser
jobsSchema = """Create table if not exists requests(id int NOT NULL PRIMARY KEY AUTO_INCREMENT, status varchar(60), name varchar(100),created_by INT, notifications varchar(300), timezone varchar(10), request VARCHAR(300), request_interval_seconds smallint, tolerated_failures smallint, is_active bool, created DATETIME, updated DATETIME);"""
jobsColumn = """(`status`, `name`, `created_by`, `notifications`, `timezone`, `request`, `request_interval_seconds`, `is_active`, `tolerated_failures`, `created`, `updated`)"""
userSchema = """Create table if not exists users(id BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT, photoUrl VARCHAR(100), name VARCHAR(50), label VARCHAR(50), type VARCHAR(30));"""
usersColumn = """(`photoUrl`, `name`, `label`, `type`)"""
tasksSchema = """Create table if not exists tasks(id int NOT NULL PRIMARY KEY AUTO_INCREMENT, task_name VARCHAR(60),task_id int, task_status VARCHAR(50), task_last_run DATETIME); """
tasksColumn = """(task_name, task_id, task_status, task_last_run)"""
class DataBase(Config):
    
    def __init__(self,*args, **kwargs):
        super(DataBase, self).__init__()
        self.host = self.config.get('dbUrl')
        self.database = self.config.get('dbName')
        self.username = self.config.get('dbUsername')
        self.password = self.config.get('dbPassword')

    def connection(self):
        db = mysql.connect(host=self.host,
                             user=self.username,
                             passwd=self.password,
                             db=self.database,
                             auth_plugin='mysql_native_password')
        db.autocommit = True
        return db

    def cursor(self, connection):
        return connection.cursor(dictionary=True)

    def get_coloumn_definition(self, table_name):
        if table_name == 'users':
            return usersColumn
        elif table_name == 'requests':
            return jobsColumn
        elif table_name == 'tasks':
            return tasksColumn

    def put_data_into_table(self, table_name, data):
        columns = self.get_coloumn_definition(table_name).replace('(','').replace(')','')
        resultSet = self.execute_query(f"select * from {table_name} where id = {data['id']}")
        if resultSet:
            sql = f"""update {table_name} set"""
            updated = datetime.datetime.now()
            data['updated'] = updated
            data['created'] = date_parser.parse(data['created'])
            for column in columns.split(','):
                column = column.replace('`','').strip()
                sql = sql+ f" {column} = '{data[column]}',"
            sql = sql[0:len(sql)-1]+f' where id = {data["id"]};'
        else:
            r = data
            sql = f"insert into requests {jobsColumn} values('{r['status']}', '{r['name']}',99, '{r['notifications']}', '{r['timezone']}','{r['request']}','{r['request_interval_seconds']}', 1, '{r['tolerated_failures']}','{datetime.datetime.now()}', '{datetime.datetime.now()}');"
        print(sql)
        self.execute_query(sql)
        return []

    def get_data_from_table(self, table_name, params=None):
        query = f"select `id`, {self.get_coloumn_definition(table_name).replace('(','').replace(')','')} from {table_name}"
        if params:
            condition = " where "
            for key,value in params.items():
                condition = condition + f"{key} = {value}"
            query = query + condition
        if table_name == 'requests':
            query = query + ' order by updated desc'
        query = query + ";"
        return self.execute_query(query)

    def execute_query(self, query, params=None):
        try:
            conn = self.connection()
            cursor = self.cursor(conn)
            self.execute(cursor, query)
            results = cursor.fetchall()
            conn.commit()
            conn.close()
            return results
        except Exception as e:
            print(e)
            return []

    def execute(self, cursor, query, params=None):
        try:
            cursor.execute(query, params)
            print('Execution done')
        except Exception as e:
            print('error occurred', e)

    def setup_db(self):
        conn = self.connection()
        cursor = self.cursor(conn)
        self.execute(cursor, jobsSchema)
        self.execute(cursor, userSchema)
        self.execute(cursor, tasksSchema)
