import psycopg2

DATABASE = "test_db"
USER = "postgres"
PASSWORD = "hoge"
HOST = "127.0.0.1"
PORT = "5432"

# databases
sql = "select datname, datdba, encoding, datcollate, datctype from pg_database;"

# schemas
sql = "select nspname, nspowner, nspacl from pg_namespace;"

# roles
sql = "select rolname, rolsuper, rolcanlogin from pg_roles;"

# tables
# sql = "select schemaname, tablename from pg_tables WHERE schemaname='test';"

# tiggers
sql = "select * FROM pg_trigger;"

# トリガーに紐づく関数/プロシージャの確認
# sql = """
# SELECT tgname, proname FROM pg_trigger t, pg_proc f where t.tgfoid = f.oid and tgname = '{トリガ名}';
# """

# 関数の内容確認
# sql = "SELECT prosrc FROM pg_proc WHERE proname = '{関数名}';"

# テーブル定義
sql = """
SELECT table_name, column_name, data_type, is_nullable, character_maximum_length
FROM information_schema.columns
WHERE table_name = 'machine'
AND TABLE_SCHEMA='test'
"""

# ?
sql = """
SELECT *
FROM information_schema.element_types
WHERE table_name = 'machine'
"""

# views
# sql = """
# SELECT schemaname, viewname FROM pg_views where "viewowner" = 'postgres' ORDER BY viewname
# """


sql = "create database store_4316;"

def connect_database():
    conn = psycopg2.connect(
        database = DATABASE,
        user = USER,
        password = PASSWORD,
        host = HOST,
        port = PORT
    )
    conn.autocommit = True
    return conn

conn = connect_database()
cur = conn.cursor()
cur.execute(sql)

data = cur.fetchall() # 出力結果
print(data)

# dbとカーソルを閉じる
cur.close()
conn.close()