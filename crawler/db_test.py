# 1. initialize the db
import sqlite3
import db
db.init_cursorcon()
from db import cursor, con
db.init_db()

# 2. insert new link
db.insert_link("https://www.google.com")
db.print_db()

# 3. extract link to visit
newLink = db.get_link()
print("Link:", newLink)
newLink = db.get_link()
print("Link:", newLink)

# 4. update link params
db.update_link(newLink, 0.500, "192.168.10.1", "geolocation")
db.print_db()

# 5. update keyword params
db.insert_keyword("Ball", "Asia")
db.insert_keyword("Ball", "Asia")
db.insert_keyword("Ball", "NA")
db.insert_keyword("Not ball", "NA")
db.insert_keyword("Not ball", "SA")
db.print_db()
res = db.get_keywords()
print(res)