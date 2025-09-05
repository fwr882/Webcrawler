from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import requests
from requests.exceptions import RequestException, HTTPError
import asyncio
import aiohttp






def normalize_url(url):
    input_url = urlparse(url)
    Normalized = input_url.netloc + input_url.path
    if Normalized.endswith("/"):
        return Normalized[:-1]
    return Normalized

def get_h1_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    h1_tag = soup.find('h1')
    if h1_tag:
        # Get just the direct text of the h1 tag
        return h1_tag.get_text(strip=True, separator=' ').split('\n')[0]
    else:
        return None
    
def get_first_paragraph_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    main_tag = soup.find('main') 
    p_tag = soup.find('p')     
    if main_tag:
        first_paragraph = main_tag.find('p')
        return first_paragraph.get_text()
    elif p_tag:
        first_paragraph = p_tag
        return first_paragraph.get_text()
    else:
        return None

def get_urls_from_html(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    urls = soup.find_all('a')
    absolute_urls = []
    for a in urls:
        href = a.get('href')
        if href:
            absolute_url = urljoin(base_url, href)
            absolute_urls.append(absolute_url)
    try:
        # Filter out None and invalid URLs
        absolute_urls = [url for url in absolute_urls if url and urlparse(url).netloc]
        return absolute_urls
    except Exception as e:
        print(f"Error processing URLs: {str(e)}")
        return []
    
    
    
def get_images_from_html(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    images = soup.find_all('img')
    absolute_images = []
    for img in images:
        src = img.get('src')
        if src:
            absolute_url = urljoin(base_url, src)
            absolute_images.append(absolute_url)
    try:
        # Filter out None and invalid URLs
        absolute_images = [url for url in absolute_images if url and urlparse(url).netloc]
        return absolute_images
    except Exception as e:
        print(f"Error processing image URLs: {str(e)}")
        return []

def extract_page_data(html, page_url):
    try:
        return {
            "url": page_url,
            "h1": get_h1_from_html(html),
            "first_paragraph": get_first_paragraph_from_html(html),
            "outgoing_links": get_urls_from_html(html, page_url),
            "image_urls": get_images_from_html(html, page_url)
        }
    except Exception as e:
        print(f"Error extracting page data: {str(e)}")
        return {
            "url": page_url,
            "h1": None,
            "first_paragraph": None,
            "outgoing_links": [],
            "image_urls": []
        }
        
#filter links to only those that look like html
def looks_like_html(u: str) -> bool:
    path = urlparse(u).path.lower()
    return not path.endswith((".xml", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".css", ".js", ".ico", ".pdf"))


async def crawl_site_async(base_url, max_concurrency, max_pages):
        async with AsyncCrawler(base_url, max_concurrency, max_pages) as crawler:
            return await crawler.crawl()
   

class AsyncCrawler:
    def __init__(self, base_url, page_data=None, max_concurrency=10, max_pages=100):
        self.base_url = base_url
        self.base_domain = urlparse(base_url).netloc
        self.page_data = {}
        self.lock = asyncio.Lock()
        self.max_concurrency = max_concurrency
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.session = None
        self.max_pages = max_pages
        self.should_stop = False
        self.all_tasks = set()
        
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc, tb):
        await self.session.close()
        
    async def add_page_visit(self, url):
        norm= normalize_url(url)
        async with self.lock:
            if self.should_stop:
                return False
            if norm in self.page_data:
                return False
            
                       
            # claim so that other coroutines wont crawl
            self.page_data[norm] = None
            
        
            if len(self.page_data) >= self.max_pages:
                    self.should_stop = True
                    print("Reached maximum number of pages to crawl.")
                    
            return True
            
            
        
    
    async def get_html(self, url):
        async with self.session.get(url, headers={"User-Agent": "BootCrawler/1.0"}, timeout=10) as resp:
            if resp.status >= 400:
                raise Exception(f"HTTP error: {resp.status}")
            ct = resp.headers.get("Content-Type", "").lower()
            if "text/html" not in ct:
                return None  # skip
            return await resp.text()
    
        
    async def crawl_page(self, url):
        if self.should_stop:
            return
        current = asyncio.current_task()
        self.all_tasks.add(current)
        try:
              
        #check if the current url is in the same domain as the base url
            if urlparse(url).netloc != self.base_domain:
                return
           
            
            first = await self.add_page_visit(url)
            if not first:
                return
         
            #fetch the html under a semaphore
            async with self.semaphore:
                html = await self.get_html(url)
            if not html:
                return
        
        
            #extract and store the page data under a lock
            data = extract_page_data(html, url)
            norm = normalize_url(url)
            async with self.lock:
                self.page_data[norm] = data
            print(f"crawled: {norm}")
            
            print(f"links: {len(get_urls_from_html(html, url))} on {norm}")
            #spawn child tasks and await for them to complete
            tasks = []
            for link in get_urls_from_html(html, url):
                if urlparse(link).netloc == self.base_domain and looks_like_html(link):
                    t = asyncio.create_task(self.crawl_page(link))
                    self.all_tasks.add(t)
                    tasks.append(t)
                    
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
                
        #allows graceful shutdown
        except asyncio.CancelledError:
            return
                
        finally:
            self.all_tasks.discard(current)
          
        
            
    async def crawl(self):
        await self.crawl_page(self.base_url)
        return self.page_data
    
    
    
        

          
            
            
         
        
        
        
    
    
    
        
        
    