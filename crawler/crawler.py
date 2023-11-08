import logging
import re
import socket
import base64
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from fake_useragent import UserAgent

# Initialise random user agent generator
ua = UserAgent()


def retrive_google_news_url(url: str) -> str:
    """Retrieve the Base64 encoded website URL from Google News"""
    url_prefix = re.compile(fr"^{re.escape('https://news.google.com/articles/')}(?P<encoded_url>[^?]+)")
    decoded_url_prefix = re.compile(rb'^\x08\x13".+?(?P<primary_url>http[^\xd2]+)\xd2\x01')

    match = url_prefix.match(url)
    if match:
        encoded_text = match.groupdict()["encoded_url"] 
        encoded_text += "===" 
        decoded_text = base64.urlsafe_b64decode(encoded_text)

        match = decoded_url_prefix.match(decoded_text)

        if match:
            primary_url = match.groupdict()["primary_url"]
            primary_url = primary_url.decode()
            return primary_url


def crawler(url, keywords):
    """Crawler method, returns URL visited, server response time, IP address, geolocation and counts of keywords matched of URL visited"""
    urls_set = set()
    keywords_count = []

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'cache-control': 'no-cache',
        'dnt': '1',
        'pragma': 'no-cache',
        'user-agent': ua.random, # Get random user agent for each request
    }

    try:
        domain = urlparse(url).netloc
        ip_addr = socket.gethostbyname(domain)

        response = requests.get(url, headers=headers)
        # Raise exception if response status code is not 200
        response.raise_for_status()
        response_time = response.elapsed.total_seconds()

        # Filter URLs from Reddit
        if domain == 'old.reddit.com' and 'over18' in response.url:
            raise Exception(f"{url} is now filtered")

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # Only scrap links from #siteTable element
            if domain == 'old.reddit.com':
                link_elements = soup.find('div', {'id': 'siteTable'}).find_all('a', href=True)
            # Only scrap links from main element
            elif domain == 'news.google.com':
                link_elements = soup.find('main').find_all('a', href=True)
            else:
                link_elements = []
                for div in soup.find('body').find_all('div'):
                    # Scrap links which are not in header and footer
                    if 'header' not in div.parent and 'footer' not in div.parent:
                        link_elements += div.find_all('a', href=True)

            for link in link_elements:
                href = link['href']
                if href != '':
                    if href[0] == '.':
                        href = href[1:]
                    # Add URL scheme and domain to incomplete URLs scrapped
                    if not href.startswith('http'):
                        base_url = urlparse(url).scheme + "://" + domain
                        href = f"{base_url}{href}"
                    # Retrieve the Base64 encoded website URL from Google News article links
                    if 'https://news.google.com/articles/' in href:
                        href = retrive_google_news_url(href)
                    if href and re.match(r'^https?://', href):
                        urls_set.add(href)

            # Obtain geolocation of server from API
            geolocation_response = requests.get(f'http://ip-api.com/json/{ip_addr}?fields=2113542')
            # Raise exception if response status code is not 200
            geolocation_response.raise_for_status()

            for keyword in keywords:
                keywords_count.append({'keyword': keyword, 'count': soup.text.lower().count(keyword.lower())})

            if geolocation_response.status_code == 200:
                geolocation_response_json = geolocation_response.json()
                # To identify the popularity by continent
                geolocation_continent = geolocation_response_json['continentCode']
                # To store the web server's geolocation by country
                geolocation_country = geolocation_response_json['countryCode']

                logging.info(f"Succesfully fetched {url}: Response time: {response_time}s | IP Address: {ip_addr} | Geolocation: {geolocation_country}")

                return url, response_time, ip_addr, geolocation_continent, geolocation_country, urls_set, keywords_count
    except requests.exceptions.HTTPError as e:
        logging.exception(f"Error fetching {url}: {e.response.status_code}")
        return url, None, None, None, None, urls_set, []
    except requests.exceptions.RequestException as e:
        logging.exception(f"Error connecting to {url}: {e}")
        return url, None, None, None, None, urls_set, []
    except Exception as e:
        logging.exception(f"An error occured: {e}")
        return url, None, None, None, None, urls_set, []
