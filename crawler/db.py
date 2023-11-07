import sqlite3

# initializes the database, creating tables and deleting all previous records
def init_cursorcon() -> None:
    global con, cursor
    con = sqlite3.connect("database.db")
    cursor = con.cursor()

def init_db() -> None:
    cursor.execute("DROP TABLE IF EXISTS websites")
    cursor.execute("DROP TABLE IF EXISTS keywords")
    cursor.execute("CREATE TABLE websites(link UNIQUE, isVisited, responseTime, ipAddress, geolocation)")
    cursor.execute("CREATE TABLE keywords(keyword, continent)")
    con.commit()

# inserts a new link into the database
# returns true on successful insert
def insert_link(link: str) -> bool:
    try:
        cursor.execute("""
            INSERT INTO websites (link, isVisited) 
            VALUES (?,?)
            """, (link, False))
        con.commit()
        return True
    except sqlite3.IntegrityError:
        return False


# retrieves an unvisited link from the database
# if no link exists, returns an empty string
def get_link() -> str:
    cursor.execute("""
        SELECT link FROM websites 
        WHERE isVisited = False
        LIMIT 1
        """)
    
    res = cursor.fetchone()

    if res is None:
        return ""
    else:
        res = res[0]
        cursor.execute("""
            UPDATE websites
            SET isVisited = True
            WHERE link = (?)
            """, (res,))
        con.commit()

        return res

# updates the input link with params retrieved from crawler
def update_link(link: str, responseTime: float, ipAddress: str, geolocation: str) -> None:
    cursor.execute("""
        UPDATE websites
        SET responseTime = (?), ipAddress = (?), geolocation = (?)
        WHERE link=(?)
        """, (responseTime, ipAddress, geolocation, link))
    con.commit()

# updates the keywords table
def insert_keyword(keyword:str, continent:str) -> None:
    cursor.execute("""
        INSERT INTO keywords
        VALUES (?, ?)
        """, (keyword, continent))
    con.commit()
    
# prints the db
def print_db() -> None:
    print("-" * 20)

    print("Website:")
    cursor.execute("SELECT * from websites")
    for i in cursor.fetchall():
        print(i)
    
    print()

    print("| Key | Continent | Count |")
    cursor.execute("""
        SELECT keyword, continent, count(keyword) as count 
        FROM keywords 
        GROUP BY keyword, continent
        ORDER BY keyword, continent
        """)
    for i in cursor.fetchall():
        print(i)
    print("-" * 20)

# retrieves results of keywords
def get_keywords() -> dict:
    res = {}
    cursor.execute("""
        SELECT keyword, continent, count(keyword) as count 
        FROM keywords 
        GROUP BY keyword, continent
        ORDER BY keyword, continent
        """)
    for i in cursor.fetchall():
        res[(i[0], i[1])] = i[2]

    return res

