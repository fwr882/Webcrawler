import csv

def write_csv_report(page_data, filename="report.csv"):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["page_url", "h1", "first_paragraph", "outgoing_link_urls", "image_urls"])
        writer.writeheader()
        for data in page_data.values():
            if not data:
                continue
            writer.writerow({
                "page_url": data.get("url", ""),
                "h1": data.get("h1", ""),
                "first_paragraph": data.get("first_paragraph", ""),
                "outgoing_link_urls": ";".join(data.get("outgoing_links", [])),
                "image_urls": ";".join(data.get("image_urls", []))
            })
    
    