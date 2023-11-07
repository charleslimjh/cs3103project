# Database User Guide

## Database Schema
`CREATE TABLE websites(link UNIQUE, isVisited, responseTime, ipAddress, geolocation)`

`CREATE TABLE keywords(keyword, continent)`

## Initializing the Database

1. import sqlite3 and db in the crawler
2. run db.init_cursorcon() to initialize the cursor and connection objects
3. import the cursor and con object from db
4. intialize the db using db.init_db()

Copy the following 5 lines of code to the top of your crawler.py file:

```
import sqlite3
import db

db.init_cursorcon()
from db import cursor, con
db.init_db()
```

## Database Commands Summary

- `init_db()` : resets all tables and entries
  
- `insert_link(link)` : inserts a new website into the websites table
  - If the link already exists, no insertion will occur.

- `get_link()` : retrieves an unvisited webpage into the websites table
  - If no unvisited links remain, the function returns an empty string.

- `update_link(link, responseTime, ipAddress, geolocation)` : updates the websites table with the appropriate information

- `insert_keyword(keyword, continent)` : inserts (keyword, continent) pair into the keywords table

- `print_db()` : prints out the contents of the two tables

- `get_keywords()` : returns a dictionary of the keywords table aggregated by keyword and continent

