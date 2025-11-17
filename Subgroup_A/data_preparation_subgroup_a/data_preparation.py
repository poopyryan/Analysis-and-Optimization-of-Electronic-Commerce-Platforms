import sqlite3

def write_data_using_sql_query(database_path, query):
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    connection.close()
