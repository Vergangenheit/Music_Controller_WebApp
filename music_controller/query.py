import sqlite3
from sqlite3 import Connection, Cursor

def create_connection(db_file: str) -> Connection:
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn: Connection = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn

def select_all_tasks(conn: Connection):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur: Cursor = conn.cursor()
    cur.execute("SELECT * FROM spotify_spotifytoken")

    rows: list = cur.fetchall()

    for row in rows:
        print(row)

def sql_fetch():
    con: Connection = sqlite3.connect("db.sqlite3")
    cursorObj: Cursor = con.cursor()

    cursorObj.execute('SELECT name from sqlite_master where type= "table"')

    print(cursorObj.fetchall())

def main():
    database: str = "db.sqlite3"

    # create a database connection
    conn: Connection = create_connection(database)
    with conn:
        print("2. Query all tasks")
        select_all_tasks(conn)

if __name__ == "__main__":
    main()