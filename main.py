# python
import sys
from crawl import crawl_page

def main():
    if len(sys.argv) < 2:
        print("no website provided")
        sys.exit(1)
    if len(sys.argv) > 2:
        print("too many arguments provided")
        sys.exit(1)

    base_url = sys.argv[1]
    print(f"starting crawl of: {base_url}")
    
    
    try:
        page_data = crawl_page(base_url)
        print("\n---Collected Data---\n")
        print(f"Number of pages found: {len(page_data)}\n")
        
        for url, data in page_data.items():
            print(f"URL: {url}")
            print(f" header: {data['h1']}")
            
        
        sys.exit(0)
    except Exception as e:
        print(f"Error fetching HTML: {str(e)}")
        sys.exit(1)
    
if __name__ == "__main__":
    main()
