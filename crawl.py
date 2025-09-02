from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup



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