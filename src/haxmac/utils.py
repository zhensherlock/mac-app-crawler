import requests
import random
from bs4 import BeautifulSoup


def generate_interval_time():
    return random.randint(50, 70)


def get_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/111.0.0.0 Safari/537.36 '
    }
    response = requests.get(url, headers)
    if response.status_code == 200:
        return response.text
    return None


def parse_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    app_blocks = soup.select('.tdb_module_loop')
    apps_list = []
    for app in app_blocks:
        app_name = app.find('h3').text.strip()
        app_desc = app.select_one('.td-excerpt').text.strip()
        app_link = app.find('h3').find('a')['href']
        app_category_link = app.select_one('.td-post-category')['href']

        app_data = {
            'name': app_name,
            'description': app_desc,
            'link': app_link,
            'category_link': app_category_link
        }

        apps_list.append(app_data)

    return {
        'soup': soup,
        'apps_list': apps_list
    }


def get_data(url):
    html = get_page(url)
    data = parse_page(html)

    return {
        'soup': data['soup'],
        'apps_list': data['apps_list']
    }
