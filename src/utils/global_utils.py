import os
import re
import cloudscraper
import random


def get_page(url, **kwargs):
    scraper = cloudscraper.create_scraper(delay=10, browser={'custom': 'ScraperBot/1.0', })
    headers = {
        'authority': 'xclient.info',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'no-cache',
        'referer': 'https://xclient.info/',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/111.0.0.0 Safari/537.36'
    }
    if kwargs and kwargs['headers'] is not None:
        headers.update(kwargs['headers'])
    kwargs.setdefault('headers', headers)
    response = scraper.get(url, **kwargs)
    if response.status_code == 200:
        return response.text
    return None


def retry_get_page(url, **kwargs):
    while True:
        try:
            return get_page(url, **kwargs)
        except:
            continue


def generate_interval_time(a=10, b=20):
    return random.randint(a, b)


def get_tag_name():
    full_ref = os.environ.get('GITHUB_REF')
    tag_prefix = 'refs/tags/'
    tag_name = full_ref[len(tag_prefix):] if full_ref.startswith(tag_prefix) else None
    return tag_name


def get_page_range(tag_name):
    if tag_name is None:
        return None
    match = re.search(r'page=(\d+)-(\d+)', tag_name)
    if match:
        return {
            'start': int(match.group(1)),
            'end': int(match.group(2))
        }
