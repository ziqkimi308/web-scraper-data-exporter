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
DEFAULT_USER_AGENT = random.choice(USER_AGENTS)
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
		headers = {'User-Agent': DEFAULT_USER_AGENT}
	
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
	"""
	find() with class_
	with attrs={}
	.text()
	.get()
	find_all()

	"""

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
	table = soup.find('table', class_='table table-striped')
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
	

# Scrap book catalog (home) with pages
def scrape_catalog(base_url, max_pages=None, fetch_details=False, headers=None, delay=DEFAULT_DELAY):
	"""
	urljoin from urllib.parse
	urljoin join 2 urls - join pattern depends on cases
	dict.update() - merge instead of append or replace

	"""

	books = []
	page_num = 1
	# urljoin from urllib.parse
	catalog_url = urljoin(base_url, "catalogue/page-{}.html")

	while True:
		if max_pages and page_num > max_pages:
			break
		
		# Dynamically updating url
		url = catalog_url.format(page_num)
		print(f"Scraping page {page_num}: {url}")

		# Fetch page
		soup = fetch_page(url, headers)
		if not soup:
			break
		
		# Find all book articles
		articles = soup.find_all('article', class_='product_pod')
		if not articles:
			break

		for article in articles:
			book = {} # not books

			# title and detail
			title_tag = article.h3.a
			if title_tag:
				book['title'] = title_tag.get('title', 'N/A') # title, href, and others included in meta data
				# urljoin() join 2 urls but does not has a fixed pattern. It depends on the case.
				detail_url = urljoin(url, title_tag.get('href', ''))
				book['detail_url'] = detail_url
			else:
				continue

			# price
			price_tag = article.find('p', class_='price_color')
			book['price'] = price_tag.text.strip() if price_tag else 'N/A'

			# rating
			rating_tag = article.find('p', class_='star-rating')
			if rating_tag:
				rating_class = rating_tag.get('class', [])
				# rating_class is a list of CSS classes, e.g. ['star-rating', 'Three']
    			# - If length == 0 → no class attribute at all
    			# - If length == 1 → only 'star-rating' present, rating info missing
    			# - If length >= 2 → second item holds rating word ('One', 'Two', etc.)
				rating = rating_class[1] if len(rating_class) > 1 else 'N/A'
				book['rating'] = rating
			else:
				book['rating'] = 'N/A'

			# availability
			avail_tag = article.find('p', class_='instock availability')
			book['availability'] = avail_tag.text.strip() if avail_tag else 'N/A'

			if fetch_details:
				print(f"Fetching details for: {book['title']}")
				details = scrape_book_details(detail_url, headers)
				if details:
					book.update(details) # update merge into existing data without replace them
				time.sleep(delay)
			
			# Update the outside books
			books.append(book)

		# Check Next page
		next_button = soup.find('li', class_='next')
		if not next_button:
			break

		page_num += 1
		time.sleep(delay)
	
	return books

# Export to json and csv
def export_to_csv(data, filename):
	"""
	csv.DictWriter(file, fieldnames)
	.writeheader()
	.writerows()
	IOError
	file=sys.stderr
	"""

	if not data:
		print("No data to export.")
		return False
	
	# data is a list of dictionaries
	fieldnames = data[0].keys()

	try:
		with open(filename, 'w', newline='', encoding='utf-8') as file:
			writer = csv.DictWriter(file, fieldnames=fieldnames)
			writer.writeheader()
			writer.writerows(data)
		print(f"Data exported to {filename} ({len(data)} records)")
		return True
	
	except IOError as e:
		print(f"Error writing CSV: {e}", file=sys.stderr)
		return False
	
def export_to_json(data, filename, indent=2):
	"""
	json.dump() - file to json
	ensure_ascii - retain non-ASCII characters
	"""

	if not data:
		print("No data to export.")
		return False
	
	try:
		with open(filename, 'w', encoding='utf-8') as file:
			json.dump(data, file, indent=indent, ensure_ascii=False)
		print(f"Data exported to {filename} ({len(data)} records)")
		return True
	except IOError as e:
		print(f"Error writing JSON: {e}", file=sys.stderr)
		return False

# CLI Integration
def main():
	# define main parser
	parser = argparse.ArgumentParser(
		description="Web Scraper & Data Exporter",
		formatter_class=argparse.RawDescriptionHelpFormatter,
		epilog="""Examples:
# Scrape book listings only (basic info) and save to CSV
python web_scraper.py --max-pages 2 --output books.csv
# Scrape with full details and export to JSON
python web_scraper.py --details --output books.json --format json
# Custom URL and delay
python web_scraper.py --url http://books.toscrape.com --delay 2
""")
	
	# define arguments
	parser.add_argument('--url', default=DEFAULT_BASE_URL, help=f"Base URL to scrape (default: {DEFAULT_BASE_URL})")

	parser.add_argument('--max-pages', type=int, default=None, help=f"Maximum number of catalog pages to scrape")

	# since boolean only has 2 values, it does not need default 
	parser.add_argument('--details', action='store_true', help=f"Fetch detailed information from each book page")

	parser.add_argument('--output', default='books_export', help="Output filename without extension (default: books_export)")

	parser.add_argument('--format', choices=['csv', 'json', 'both'], default='csv', help='Export format (default: csv)')

	parser.add_argument('--delay', type=float, default=DEFAULT_DELAY, help=f'Delay between requests in seconds (default: {DEFAULT_DELAY})')

	parser.add_argument('--user-agent', default=DEFAULT_USER_AGENT, help='Custom User-Agent string')

	# Parse/Extract arguments
	args = parser.parse_args()

	headers = {'User-Agent': str(args.user_agent)}
	print(f"Starting scraper for {args.url}")

	# Record start time
	start_time = time.time()

	data = scrape_catalog(
        base_url=args.url,
        max_pages=args.max_pages,
        fetch_details=args.details,
        headers=headers,
        delay=args.delay
    )

	# Record end time
	elapsed_time = time.time() - start_time
	print(f"Scraping completed in {elapsed_time:.2f} seconds. Total items: {len(data)}")

	if not data:
		print("No data scraped. Exiting.")
		sys.exit(1)

	# The success statement is used to accumulate success across multiple steps. 
	# Even if once success becomes False, it continues to be False even though all other steps return True
	# This is to ensure all 3 success (data, export csv, export json)

	success = True

	if args.format in ('csv', 'both'):
		csv_file = f"{args.output}.csv"
		success = export_to_csv(data, csv_file) and success
	
	if args.format in ('json', 'both'):
		json_file = f"{args.output}.json"
		success = export_to_json(data, json_file) and success

	sys.exit(0 if success else 1)

if __name__ == '__main__':
	main()