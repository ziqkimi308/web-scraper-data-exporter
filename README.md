### Overview

A lightweight Python web scraper for **Books to Scrape** that crawls the catalog, extracts book metadata, and exports results to **CSV**, **JSON**, or both. The script is CLI driven and includes configurable options for user agent, request delay, page limits, and retry behavior.

---

### Features

- **Catalog crawling** with automatic pagination handling  
- **Optional detail scraping** for each book page (title, price, availability, description, category, UPC, URL)  
- **Robust fetching** with configurable retries, timeouts, and exponential backoff delays  
- **Polite scraping** via configurable User-Agent and delay between requests  
- **Export formats**: CSV, JSON, or both  
- **Simple CLI** with clear flags for common workflows

---

### Installation

- **Requirements**  
  - Python 3.8 or newer  
  - The following Python packages: `requests`, `beautifulsoup4`

- **Install dependencies**

```bash
python -m pip install requests beautifulsoup4
```

- **Clone repository**

```bash
git clone <your-repo-url>
cd <your-repo-directory>
```

---

### Usage

- **Basic command structure**

```bash
python web_scraper.py [options]
```

- **Common examples**

```bash
# Scrape first 2 catalog pages and save to CSV
python web_scraper.py --max-pages 2 --output books --format csv

# Scrape with full book details and export to JSON
python web_scraper.py --details --output books_full --format json

# Use a custom base URL and increase delay between requests
python web_scraper.py --url https://books.toscrape.com/ --delay 2.5 --max-pages 3
```

- **CLI flags**

- `--url`  
  - **Description**: Base URL to scrape  
  - **Default**: `https://books.toscrape.com/`

- `--max-pages`  
  - **Description**: Maximum number of catalog pages to crawl

- `--details`  
  - **Description**: Fetch detailed information from each book page

- `--output`  
  - **Description**: Output filename without extension

- `--format`  
  - **Choices**: `csv`, `json`, `both`  
  - **Description**: Export format

- `--delay`  
  - **Description**: Delay between requests in seconds

- `--user-agent`  
  - **Description**: Custom User-Agent string

---

### Configuration

- **Default values** are defined at the top of the script:
  - **Base URL**: `https://books.toscrape.com/`  
  - **Default delay**: `1.0` second  
  - **Default max retries**: `3`  
  - **Default user agents**: a small rotating list used when no custom User-Agent is provided

- **Politeness and reliability tips**
  - Increase `--delay` when scraping many pages to reduce server load.  
  - Use `--user-agent` to provide a meaningful identifier.  
  - Respect `robots.txt` and site terms of service before scraping any site other than Books to Scrape.

---

### Troubleshooting and Contributing

- **No data exported**
  - Confirm the base URL is reachable in your environment.  
  - Check for network issues or site blocking.  
  - Increase verbosity by adding print statements around `fetch_page` to inspect HTTP errors.

- **Slow or failing requests**
  - Increase `--delay` and `--max-retries`.  
  - Verify your network and firewall settings.  
  - Try a different `--user-agent` value.

- **CSV or JSON write errors**
  - Ensure you have write permissions in the working directory.  
  - Confirm there is sufficient disk space and the filename is valid.


---

### Quick Reference

- **Run full scrape and export both formats**

```bash
python web_scraper.py --details --max-pages 5 --format both --output my_books
```

- **Exit codes**
  - `0` on success  
  - `1` on failure or when no data was scraped

---
