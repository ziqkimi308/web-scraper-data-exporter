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
				sleep_time = delay * (2 ** attempt) + random.uniform(0, 0.5)
				time.sleep(sleep_time)
	return None
