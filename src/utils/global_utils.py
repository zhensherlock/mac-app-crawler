import cloudscraper
import random


def get_page(url):
    scraper = cloudscraper.create_scraper(delay=10, browser={'custom': 'ScraperBot/1.0', })
    response = scraper.get(url)
    if response.status_code == 200:
        return response.text
    return None


def generate_interval_time(a=10, b=20):
    return random.randint(a, b)
