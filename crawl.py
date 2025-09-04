from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import requests
from requests.exceptions import RequestException, HTTPError





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


def get_html(url):
        resp = requests.get(url, headers={"User-Agent": "BootCrawler/1.0"}, timeout=10)
        resp.raise_for_status()  # Raise an error for bad status codes
        
        ct = resp.headers.get('Content-Type', '').lower()
        
        if "text/html" in ct:
            return resp.text
        raise ValueError(f"non-HTML content type: {ct}")
    
        
def crawl_page(base_url, current_url=None, page_data=None, fail_data=None):
    if current_url is None:
        current_url = base_url
    
    
    if page_data is None:
        page_data = {}

    #this dictionary will hold all the attempted but FAILED crawls so it doesn't attempt to crawl them again
    if fail_data is None:
        fail_data = set()
    
    #check if the current url is in the same domain as the base url
    if urlparse(base_url).netloc != urlparse(current_url).netloc:
        return
    
    
    
    normaled_url = normalize_url(current_url)
    if normaled_url in fail_data:
        print(f"skipping {current_url}, previously failed")
        return
    if normaled_url in page_data:
        print(f"skipping {current_url}, already crawled")
        return
    
    
    print(f"crawling: {current_url}...")
    try:
        html = get_html(current_url)
    except Exception as e:
        print(f"Error fetching {current_url}: {str(e)}")
        fail_data.add(normaled_url)
        return
   
    #if everything went well extract and store the page data
    
    rich_data = extract_page_data(html, current_url)
    page_data[normaled_url] = rich_data
    
    #Get all the Urls on the page and crawl them too
    urls_on_page = get_urls_from_html(html, base_url)
    for new_url in urls_on_page:
        crawl_page(base_url, new_url, page_data, fail_data)
    return page_data

          
            
            
         
        
        
        
    
    
    
        
        
    