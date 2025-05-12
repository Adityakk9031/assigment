import requests
from bs4 import BeautifulSoup
import csv
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
}

BASE_URL = "https://www.olx.in"
SEARCH_QUERY = "car cover"
OUTPUT_FILE = "olx_car_covers.csv"


def fetch_html(page=1):
    url = f"https://www.olx.in/items/q-{SEARCH_QUERY.replace(' ', '-')}\?page={page}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.text
    return None


def parse_listings(html):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    for item in soup.find_all("li", {"data-aut-id": "itemBox"}):
        title_tag = item.find("span", {"data-aut-id": "itemTitle"})
        price_tag = item.find("span", {"data-aut-id": "itemPrice"})
        location_tag = item.find("span", {"data-aut-id": "item-location"})
        link_tag = item.find("a", href=True)

        if title_tag and price_tag and location_tag and link_tag:
            title = title_tag.get_text(strip=True)
            price = price_tag.get_text(strip=True)
            location = location_tag.get_text(strip=True)
            url = BASE_URL + link_tag['href']
            listings.append((title, price, location, url))

    return listings


def scrape_all_pages(max_pages=5):
    all_listings = []
    for page in range(1, max_pages + 1):
        print(f"Scraping page {page}...")
        html = fetch_html(page)
        if not html:
            print("Failed to fetch page or no more data.")
            break
        listings = parse_listings(html)
        if not listings:
            print("No listings found on this page.")
            break
        all_listings.extend(listings)
        time.sleep(1)  # polite delay to avoid being blocked
    return all_listings


def save_to_csv(data, filename):
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Title", "Price", "Location", "URL"])
        writer.writerows(data)


def main():
    listings = scrape_all_pages(max_pages=5)
    save_to_csv(listings, OUTPUT_FILE)
    print(f"Saved {len(listings)} listings to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
