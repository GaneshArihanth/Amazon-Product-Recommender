from scrapers.amazon import scrape_amazon
from scrapers.flipkart import scrape_flipkart
from scrapers.ebay import scrape_ebay

query = "wireless mouse"

print("\n=== Amazon ===")
print(scrape_amazon(query))

print("\n=== Flipkart ===")
print(scrape_flipkart(query))

print("\n=== eBay ===")
print(scrape_ebay(query))
