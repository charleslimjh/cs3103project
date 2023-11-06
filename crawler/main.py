import argparse
import logging
import os
import sqlite3
from io import UnsupportedOperation
from urllib.parse import urlparse

import db
from crawler import crawler

limit = 30


def main():
    init_log()
    seed_urls = parse_args()
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    db.init_db(cur)

    # 2. insert new link
    for url in seed_urls:
        db.insert_link(con, cur, url)
    response_time, ip_addr, geolocation, urls_set = init_crawl(db.get_link(con, cur))
    for _ in range(len(urls_set)):
        db.insert_link(con, cur, urls_set.pop())
    db.update_link(con, cur, seed_urls[0], response_time, ip_addr, None)
    db.print_db(cur)


def parse_args() -> []:
    """Takes in the command line arguments and finds the root url(s) from the seed file given"""
    parser = argparse.ArgumentParser(prog="Web crawler",
                                     description="Multi-threaded web crawler that generates statistics from keyword "
                                                 "matching of multiple websites")
    parser.add_argument("filename", help="absolute path of file containing seed url")
    parser.add_argument("limit", help="number of urls to be found by crawler (not including seed url)", default=30)
    args = parser.parse_args()
    logging.info(f"program started with arguments provided: {args}")
    filename = os.path.abspath(args.filename)
    urls = []
    global limit
    limit = args.limit
    try:
        f = open(filename, "r")
        for line in f:
            if is_valid_url(line):
                urls.append(line)
                logging.info(f"Url added: {line}")
            else:
                raise ValueError
        logging.info(f"All urls successfully added: {urls} ")
        return urls
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


def init_crawl(urls):
    """Initialises the crawler and feeds it the root url(s)"""
    return crawler(urls)


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
