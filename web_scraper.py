from bs4 import BeautifulSoup
import requests
import csv
import json
import argparse
import sys
import time
import random
from urllib.parse import urljoin, urlparse
from datetime import datetime

# Config
DEFAULT_BASE_URL = "https://books.toscrape.com/"
USER_AGENTS = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/123 Safari/537.36",
					  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/123 Safari/537.36",
					  "Mozilla/5.0 (X11; Linux x86_64) Firefox/115.0"]
DEFAULT_USER_AGENT = {"User-Agent": random.choice(USER_AGENTS)}
DEFAULT_DELAY = 1.0
DEFAULT_MAX_RETRIES = 3

# Fetch url and scrap
def fetch_page(url, headers=None, max_retries=DEFAULT_MAX_RETRIES, delay=DEFAULT_DELAY):
	"""
	sys to separate stderr output
	requests to make requests and status code
	BeautifulSoup to parse and extract data from xml/html
	time to sleep for delay
	random to generate random float factor for delay, randomly choose user agent

	"""

	if headers is None:
		headers = DEFAULT_USER_AGENT
	
	# range() inclusive start exclusive end
	for attempt in range(max_retries):
		try:
			response = requests.get(url, headers=headers, timeout=10)
			response.raise_for_status()
			return BeautifulSoup(response.content, 'html.parser')
		
		except (requests.RequestException, ValueError) as e:
			print(f"Attempt {attempt + 1}/{max_retries} failed for {url}: {e}", file=sys.stderr)
			if attempt < max_retries - 1:
				# uniform is randint but for floats
				sleep_time = delay * (2 ** attempt) + random.uniform(0, 0.5) # gradually increase the delay for each tries
				time.sleep(sleep_time)
	return None

def scrape_book_details(book_url, headers=None):
	soup = fetch_page(book_url, headers)
	if not soup:
		return None

	data = {}

	# title
	title_tag = soup.find('h1')
	data['title'] = title_tag.text.strip() if title_tag else 'N/A'

	# price
	price_tag = soup.find('p', class_='price_color')
	data['price'] = price_tag.text.strip() if price_tag else 'N/A'

	# availability
	avail_tag = soup.find('p', class_='instock availability')
	data['availability'] = avail_tag.text.strip() if avail_tag else 'N/A'

	# product description
	prod_desc_tag = soup.find('meta', attrs={'name':'description'})
	# get() is to fetch attribute value. Can add default value
	data['description'] = prod_desc_tag.get('content', 'N/A').strip()

	# category (breadcrumb)
	breadcrumb = soup.find('ul', class_='breadcrumb')
	if breadcrumb:
		links = breadcrumb.find_all('a')
		if len(links) >= 3:
			data['category'] = links[2].text.strip()
		else:
			data['category'] = 'N/A'
	else:
		data['category'] = 'N/A'

	# upc from table
	table = soup.find('table', class_='table table-stripped')
	if table:
		for row in table.find_all('tr'):
			header = row.find('th')
			if header and header.text.strip() == 'UPC':
				data['upc'] = row.find('td').text.strip()
				break
			else:
				data['upc'] = 'N/A'
	else:
		data['upc'] = 'N/A'

	# url
	data['url'] = book_url

	return data
	

print(scrape_book_details(DEFAULT_BASE_URL))