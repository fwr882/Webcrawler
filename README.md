# Web Crawler

A Python CLI that crawls a website and generates an internal links report. Useful for auditing site architecture and finding orphaned pages.

## Features
- Crawl starting from a root URL (same-origin only)
- Extract and normalize internal links
- Generate a report of page -> outbound internal links
- Configurable crawl limits and concurrency (if applicable)
- Simple, testable design

## Requirements
- Python 3.10+
- uv (for dependency management)

## Setup
```bash

# clone
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>

# create and sync environment
uv sync

# do a basic crawl
python -m crawler <root_url> --out report.txt

# common options
python -m crawler <root_url>\
    --max-pages 500\
    --timout 10\
    --out report.txt
#Roadmap
CSV/JSON report formats
Parallel fetching with rate limiting