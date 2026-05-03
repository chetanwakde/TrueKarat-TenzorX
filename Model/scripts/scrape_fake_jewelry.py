import os
import requests
from duckduckgo_search import DDGS
from concurrent.futures import ThreadPoolExecutor

def download_image(url, filepath):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                f.write(response.content)
            return True
    except:
        pass
    return False

def scrape_images(queries, max_results_per_query=50, output_dir="raw_data/FakeJewelry"):
    os.makedirs(output_dir, exist_ok=True)
    
    urls = []
    with DDGS() as ddgs:
        for query in queries:
            print(f"Searching for: {query}")
            results = ddgs.images(query, max_results=max_results_per_query)
            for res in results:
                urls.append(res['image'])
                
    # Remove duplicates
    urls = list(set(urls))
    print(f"Found {len(urls)} unique image URLs.")
    
    downloaded = 0
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for i, url in enumerate(urls):
            filepath = os.path.join(output_dir, f"fake_{i}.jpg")
            futures.append(executor.submit(download_image, url, filepath))
            
        for future in futures:
            if future.result():
                downloaded += 1
                
    print(f"Successfully downloaded {downloaded} fake jewelry images to {output_dir}")

if __name__ == "__main__":
    queries = [
        "artificial gold jewelry amazon",
        "imitation gold bangles flipkart",
        "1 gram gold plated necklace",
        "fake gold jewelry"
    ]
    # Scrape ~200 images for the Fraud head
    base_dir = os.path.join(os.path.dirname(__file__), "..", "raw_data", "FakeJewelry")
    scrape_images(queries, max_results_per_query=50, output_dir=base_dir)
