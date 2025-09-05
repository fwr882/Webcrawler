# python
import sys
import crawl
import asyncio  

async def main_async():
    url = sys.argv[1]
    max_concurrency = int(sys.argv[2])
    max_pages = int(sys.argv[3]) 
    page_data = await crawl.crawl_site_async(url, max_concurrency, max_pages)
    for data in page_data.values():
        if data is None:
            continue
        print(data["url"], data["h1"])       
        
    
    
    
if __name__ == "__main__": asyncio.run(main_async())

