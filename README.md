# CS3103 Assignment 4 Parallel Web Crawler User Guide

### To install the requirements and run the web crawler
Open up your terminal or command prompt and run the following
```
pip install -r requirements.txt
cd crawler
python3 main.py url_file keyword_file [-l Number of urls per crawler process] [-n Number of processes]
```

---
### To view/edit list of initial URLs
Visit or edit `url.txt`

---
### To view/edit list of keywords
Visit or edit `keywords.txt`

--- 
### To view database
Open `database.db` using a SQLite DB reader

--- 
### Required modules that are not imported
Openpyxl is required for pandas to write an excel file.
If you have not installed it previously by running
```pip install -r requirements.txt```
and you have all other requirements satifisfied, you can install it separately by opening up your terminal or command prompt and run the following:
```pip install openpyxl```
