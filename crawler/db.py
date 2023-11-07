import sqlite3

# initializes the database, creating tables and deleting all previous records
def init_db() -> None:
    global cursor, con
    cursor.execute("DROP TABLE IF EXISTS websites")
    cursor.execute("DROP TABLE IF EXISTS keywords")
    cursor.execute("CREATE TABLE websites(link, isVisited, responseTime, ipAddress, geolocation, htmlData)")
    cursor.execute("CREATE TABLE keywords(keyword, continent)")
    con.commit()

# inserts a new link into the database
def insert_link(link: str) -> None:
    global cursor, con
    cursor.execute("""
        INSERT INTO websites (link, isVisited) 
        VALUES (?,?)
        """, (link, False))
    con.commit()

# retrieves an unvisited link from the database
def get_link() -> str:
    global cursor, con
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
def update_link(link: str, responseTime: float, ipAddress: str, geolocation: str) -> None:
    global cursor, con
    cursor.execute("""
        UPDATE websites
        SET responseTime = (?), ipAddress = (?), geolocation = (?)
        WHERE link=(?)
        """, (responseTime, ipAddress, geolocation, link))
    con.commit()
    
# prints the db
def print_db() -> None:
    global cursor, con
    print("Website:")
    cursor.execute("SELECT * from websites")
    print(cursor.fetchall())

    print("Keywords:")
    cursor.execute("SELECT * from keywords")
    print(cursor.fetchall())
