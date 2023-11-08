import argparse
import logging
import os
import time
from io import UnsupportedOperation
from urllib.parse import urlparse

import db
from crawler import crawler
from multiprocessing import Process, Manager

# global vars
seed_urls = set()
keywords = set()

def main():
    """Main driver of program, handles initiation of all helpers and running of crawlers"""
    global limit_val # This is the maximum number of sites visited per process
    init_log()
    parse_args()

    # Initialise connection to database
    db.init_cursorcon() 
    db.init_db()

    # Add initial urls
    for url in seed_urls:
        db.insert_link(url)

    # Array to keep track of processes
    processes = []

    # Manager allows for mutex needed for database access control
    with Manager() as manager:
        database_lock = manager.Lock()
        
        # Initialise the paralised processes to crawl websites
        for _ in range(num_processes):
            process = Process(target=crawl_worker, args=(keywords, database_lock, limit_val))
            processes.append(process)
            process.start()

        # Wait for all processes to finish
        for process in processes:
            process.join()

    # Display final count of keywords and geolocation found
    print(db.get_keywords())

# Method for process to start crawlling
def crawl_worker(keywords, database_lock, max_num_crawl):
    num_crawled = 0 # Count for number of URLs crawled by child processes

    # Initialise logger for child processes
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S'
                        )

    # Initialise connection to database
    db.init_cursorcon()

    # Checks for number of URLs crawld
    while num_crawled < max_num_crawl:
        # Mutex to prevent database race conditions
        with database_lock:
            # Receive a unvisited link form the database
            link = db.get_link()
            if link == "" or link is None:
                time.sleep(5)
                continue
        
        # Display number of URLs left per child processes
        logging.info(f"Number of URLs left to crawl: {max_num_crawl - (num_crawled + 1)}")

        # Call to crawler method
        url, response_time, ip_addr, geolocation_continent, geolocation_country, urls_set, keywords_count = crawler(link, keywords)

        # Mutex to prevent database race conditions
        with database_lock:
            # Insert links scrapped from URL
            for _ in range(len(urls_set)):
                db.insert_link(urls_set.pop())

            # Update URL information
            db.update_link(url, response_time, ip_addr, geolocation_country)

            # Insert keywords found in URL 
            for keyword_count in keywords_count:
                for _ in range(keyword_count['count']):
                    db.insert_keyword(keyword_count['keyword'], geolocation_continent)

        # Delay to prevent red-limiting by websites
        time.sleep(5)

        # Increment number of URls crawled
        num_crawled += 1


def parse_args() -> []:
    """Takes in the command line arguments and finds the root url(s) from the seed file given"""
    parser = argparse.ArgumentParser(prog="Web crawler",
                                     description="Multi-threaded web crawler that generates statistics from keyword "
                                                 "matching of multiple websites")
    parser.add_argument("url_file", help="Path of file containing seed url")
    parser.add_argument("keyword_file", help="Path of file containing keywords to search websites for")
    parser.add_argument("-l", help="Number of urls to be found by each crawler process", required=False,
                        default=30)
    parser.add_argument("-n", help ="Number of processes for crawling", required=False, default=4)

    args = parser.parse_args()
    logging.info(f"program started with arguments provided: {args}")

    seed_file = os.path.abspath(args.url_file)
    keyword_file = os.path.abspath(args.keyword_file)

    global limit_val
    limit_val = int(args.l)

    global num_processes
    num_processes = int(args.n)

    try:
        f = open(seed_file, "r")
        for line in f:
            # Remove newline character
            line = line.replace("\n", "")
            if is_valid_url(line):
                seed_urls.add(line)
                logging.info(f"Url added: {line}")
            else:
                raise ValueError
        logging.info(f"All urls successfully added: {seed_urls} ")
        f = open(keyword_file, "r")
        for line in f:
            # Remove newline character
            line = line.replace("\n", "")
            keywords.add(line)
            logging.info(f"Keyword added: {line}")
        logging.info(f"All keywords successfully added: {keywords}")
    except FileNotFoundError:
        logging.exception("The file does not exist.")
    except PermissionError:
        logging.exception("Permission denied to open the file.")
    except IsADirectoryError:
        logging.exception("The path points to a directory, not a file.")
    except UnsupportedOperation:
        logging.exception("Unsupported file operation.")
    except OSError as e:
        logging.exception(f"An error occurred: {e}")
    except ValueError as e:
        logging.exception(f"Url not valid: {line}")


def init_log():
    """Initialises the logger"""
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S'
                        )


def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


if __name__ == "__main__":
    main()