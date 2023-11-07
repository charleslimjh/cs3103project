# To use the database:
# 1. import sqlite3 and db in the crawler
# 2. run db.init_cursorcon() to initialize the cursor and connection objects
# 3. import the cursor and con object from db
# 4. intialize the db using db.init_db()

# Copy the following 5 lines of code to the top of your crawler.py file
'''
import sqlite3
import db
db.init_cursorcon()
from db import cursor, con
db.init_db()
'''

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
db.print_db()
print(newLink)

# 4. update link params
db.update_link(newLink, 0.500, "192.168.10.1", "insert some data here")
db.print_db()