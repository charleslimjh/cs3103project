from crawler import db
from multiprocessing import Process, Manager

def db_read_write_test(database_lock, max_num_crawled):
    """Method to simulate reading and writing to the DB with a mutex"""
    num_crawled = 0

    # Initialise connection to database for each child process
    db.init_cursorcon()

    # Checks for number of URLs crawled
    while num_crawled < max_num_crawled:
        # Mutex to prevent database race conditions
        with database_lock:
            # Receive a unvisited link form the database
            link = db.get_link()
            if link == "" or link is None:
                continue

        # Mutex to prevent database race conditions
        with database_lock:
            # Update URL information
            db.update_link(link, None, None, None)

        # Increment number of URls crawled
        num_crawled += 1

def run(num_links):
    """Insert links into the database and initialize the child processes to read and write to the DB"""
    num_processes = 10

    db.init_cursorcon()
    db.init_db()

    for i in range(num_links):
        db.insert_link(f'https://example.com/{i}')

    # Array to keep track of processes
    processes = []

    # Manager allows for mutex needed for database access control
    with Manager() as manager:
        database_lock = manager.Lock()
        
        # Initialise the parallelised processes to crawl websites
        for _ in range(num_processes):
            process = Process(target=db_read_write_test, args=(database_lock, int(num_links / num_processes)))
            processes.append(process)
            process.start()

        # Wait for all processes to finish
        for process in processes:
            process.join()

    return db.get_num_urls_visited()