import requests
import random
import re
from bs4 import BeautifulSoup

from src.utils.sqlite import SQLiteDB


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
        app_title = app.find('h3').text.strip()
        app_desc = app.select_one('.td-excerpt').text.strip()
        app_detail_link = app.find('h3').find('a')['href']
        app_category_link = app.select_one('.td-post-category')['href']

        app_data = {
            'title': app_title,
            'description': app_desc,
            'detail_link': app_detail_link,
            'category_link': app_category_link
        }

        apps_list.append(app_data)

    return {
        'soup': soup,
        'apps_list': apps_list
    }


def get_data(url):
    html = get_page(url)
    if html is None:
        return None
    data = parse_page(html)

    return {
        'soup': data['soup'],
        'apps_list': data['apps_list']
    }


def handle_list(data):
    for row in data:
        handle_row_data(row)


def handle_row_data(row_data):
    title = row_data['title']
    regex = r"(\w+(?:\s+\w+)*)\s+(\d+\.\d+\.\d+)"
    match = re.match(regex, title)
    name, version = match.group(1), match.group(2)
    data = {
        'title': title,
        'name': name,
        'latest_version': version,
        'description': row_data['description'],
        'detail_link': row_data['detail_link'],
        'category_link': row_data['category_link'],
        'download_link': row_data['download_link']
    }
    db = SQLiteDB('haxmac.db')
    app = db.fetchone('SELECT count(1) FROM mac_app_info WHERE name = ?', name)

    return data


def insert_data(data):
    db = SQLiteDB('haxmac.db')
    db.execute(
        'INSERT INTO mac_app_info (name, version, description, download_link, source) VALUES (?, ?, ?, ?, ?)',
        (
            data['name'],
            data['version'],
            data['description'],
            data['download_link'],
            data['source']
        )
    )
