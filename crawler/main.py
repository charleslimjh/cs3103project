import argparse
import logging
import os
import time
from io import UnsupportedOperation
from urllib.parse import urlparse

import db
from crawler import crawler

# global vars
limit = 30
seed_urls = set()
keywords = set()


def main():
    """Main driver of program, handles initiation of all helpers and running of crawlers"""
    global limit
    init_log()
    parse_args()

    db.init_cursorcon()
    db.init_db()

    # Add initial urls
    for url in seed_urls:
        db.insert_link(url)
    
    while True:
        link = db.get_link()
        logging.info(f"Number of url left to crawl: {limit}")
        if link is None or limit == 0:
            break
        limit -= 1
        url, response_time, ip_addr, geolocation_continent, geolocation_country, urls_set, keywords_count = crawler(link, keywords)
        for _ in range(len(urls_set)):
            # Add new links found in the current page to the database
            db.insert_link(urls_set.pop())
        # Update current link as visited
        db.update_link(url, response_time, ip_addr, geolocation_country)
        # Insert predefined keywords found into database
        for keyword_count in keywords_count:
            for _ in range(keyword_count['count']):
                db.insert_keyword(keyword_count['keyword'], geolocation_continent)
        #db.print_db(cur)
        print(db.get_keywords())
        time.sleep(1)


def parse_args() -> []:
    """Takes in the command line arguments and finds the root url(s) from the seed file given"""
    parser = argparse.ArgumentParser(prog="Web crawler",
                                     description="Multi-threaded web crawler that generates statistics from keyword "
                                                 "matching of multiple websites")
    parser.add_argument("url_file", help="Path of file containing seed url")
    parser.add_argument("keyword_file", help="Path of file containing keywords to search websites for")
    parser.add_argument("-l", help="Number of urls to be found by crawler (not including seed url)", required=False,
                        default=30)
    args = parser.parse_args()
    logging.info(f"program started with arguments provided: {args}")
    seed_file = os.path.abspath(args.url_file)
    keyword_file = os.path.abspath(args.keyword_file)
    global limit
    limit = int(args.l)
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
