import sqlite3
import db

# 1. test create db
con = sqlite3.connect("database.db")
cur = con.cursor()
db.init_db(cur)

# 2. insert new link
db.insert_link(con, cur, "https://www.google.com")
db.print_db(cur)

# 3. extract link to visit
newLink = db.get_link(con, cur)
db.print_db(cur)
print(newLink)

# 4. update link params
db.update_link(con, cur, newLink, 0.500, "192.168.10.1", "insert some data here")
db.print_db(cur)