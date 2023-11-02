import sqlite3

# initializes the database, creating tables and deleting all previous records
def init_db(cursor: sqlite3.Cursor) -> (sqlite3.Connection, sqlite3.Cursor):
    cursor.execute("CREATE TABLE IF NOT EXISTS websites(link, isVisited, responseTime, ipAddress, htmlData)")
    cursor.execute("DELETE FROM websites")

# inserts a new link into the database
def insert_link(con: sqlite3.Connection, cursor: sqlite3.Cursor, link: str) -> None:
    cursor.execute("""
        INSERT INTO websites (link, isVisited) 
        VALUES (?,?)
        """, (link, False))
    con.commit()

# retrieves an unvisited link from the database
def get_link(con: sqlite3.Connection, cursor: sqlite3.Cursor) -> str:
    cursor.execute("""
        SELECT link FROM websites 
        WHERE isVisited = False
        LIMIT 1
        """)
    res = cursor.fetchone()[0]

    cursor.execute("""
        UPDATE websites
        SET isVisited = True
        WHERE link = (?)
        """, (res,))
    con.commit()

    return res

# updates the input link with params retrieved from crawler
def update_link(con: sqlite3.Connection, cursor: sqlite3.Cursor, link: str, responseTime: float, ipAddress: str, htmlData: str) -> None:
    cursor.execute("""
        UPDATE websites
        SET responseTime = (?), ipAddress = (?), htmlData = (?)
        WHERE link=(?)
        """, (responseTime, ipAddress, htmlData, link))
    con.commit()
    
# prints the db
def print_db(cursor: sqlite3.Cursor) -> None:
    cursor.execute("SELECT * from websites")
    print(cursor.fetchall())
