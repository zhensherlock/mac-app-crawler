import sqlite3

# 创建一个连接对象，连接到指定的 SQLite 数据库文件
conn = sqlite3.connect('haxmac.db')

# 创建一个游标对象（cursor），用于执行 SQL 语句
cur = conn.cursor()

# 查询所有数据
cur.execute('SELECT * FROM <table_name>')

# 获取结果集中的所有行，并打印每一行
rows = cur.fetchall()
for row in rows:
    print(row)

# 关闭游标和连接对象
cur.close()
conn.close()