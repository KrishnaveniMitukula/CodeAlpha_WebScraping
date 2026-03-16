import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Configuration
BASE_URL = "http://books.toscrape.com/catalogue/"
START_URL = "http://books.toscrape.com/catalogue/page-1.html"
MAX_PAGES = 5
OUTPUT_FILE = "books_dataset.csv"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; CodeAlphaBot/1.0)"}

# Fetch page
def fetch_page(url):
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")

# Parse books
def parse_books(soup):
    books = []
    articles = soup.find_all("article", class_="product_pod")
    for article in articles:
        title = article.h3.a["title"]
        price = article.find("p", class_="price_color").text.strip()
        rating_word = article.find("p", class_="star-rating")["class"][1]
        rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
        rating = rating_map.get(rating_word, 0)
        availability = article.find("p", class_="instock availability").text.strip()
        books.append({
            "Title": title,
            "Price (£)": float(price.replace("£", "").replace("Â", "")),
            "Rating (out of 5)": rating,
            "Availability": availability
        })
    return books

# Get next page
def get_next_page(soup):
    next_btn = soup.find("li", class_="next")
    if next_btn:
        return BASE_URL + next_btn.a["href"]
    return None

# Main scraping loop
def scrape_books(start_url, max_pages):
    all_books = []
    url = start_url
    page_num = 1
    while url and page_num <= max_pages:
        print(f"📄 Scraping page {page_num}...")
        soup = fetch_page(url)
        books = parse_books(soup)
        all_books.extend(books)
        print(f"   ✅ {len(books)} books found (Total: {len(all_books)})")
        url = get_next_page(soup)
        page_num += 1
        time.sleep(1)
    return all_books

# Run everything
print("🌐 Starting Scraper...\n")
books_data = scrape_books(START_URL, MAX_PAGES)

df = pd.DataFrame(books_data)
df.to_csv(OUTPUT_FILE, index=False)

print(f"\n💾 Saved {len(df)} books to '{OUTPUT_FILE}'")
print(f"\n📊 SUMMARY:")
print(f"   Total Books   : {len(df)}")
print(f"   Avg Price     : £{df['Price (£)'].mean():.2f}")
print(f"   Highest Price : £{df['Price (£)'].max():.2f}")
print(f"   Lowest Price  : £{df['Price (£)'].min():.2f}")
print(f"   Avg Rating    : {df['Rating (out of 5)'].mean():.2f} / 5")
print("\n✅ Task 1 COMPLETE!")