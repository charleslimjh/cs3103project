import requests
import socket
import re
import logging
from urllib.parse import urlparse
from bs4 import BeautifulSoup


def crawler(url):
    urls_set = set()
    try:
        response = requests.get(url)
        response.raise_for_status()
        response_time = response.elapsed.total_seconds()

        domain = urlparse(url).netloc
        ip_addr = socket.gethostbyname(domain)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            if domain == 'en.wikipedia.org':
                link_elements = soup.find('div', {'class': 'reflist'}).find_all('a', href=True)
            else:
                link_elements = soup.find_all('a', href=True)

            for link in link_elements:
                href = link['href']
                if not href.startswith('http'):
                    base_url = urlparse(url).scheme + "://" + urlparse(url).netloc
                    href = f"{base_url}{href}"
                if re.match(r'^https?://', href) and domain not in href:
                    urls_set.add(href)

            geolocation_response = requests.get(f'http://ip-api.com/json/{ip_addr}?fields=49182')
            geolocation_response.raise_for_status()

            if geolocation_response.status_code == 200:
                geolocation_response_json = geolocation_response.json()
                geolocation = geolocation_response_json['countryCode']

                return response_time, ip_addr, geolocation, urls_set
    except Exception as e:
        # Some function to log error
        logging.exception(f"Error occured: {e}")
