# import requests
import random
import re
from bs4 import BeautifulSoup
import cloudscraper
from utils import sqlite


def generate_interval_time():
    return random.randint(50, 70)


def get_page(url):
    # headers = {
    #     'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
    #                   'Chrome/111.0.0.0 Safari/537.36',
    #     'Referer': 'https://www.google.com/',
    #     'Cookie': ''
    # }
    # response = requests.get(url, headers)
    scraper = cloudscraper.create_scraper(delay=10, browser={'custom': 'ScraperBot/1.0', })
    response = scraper.get(url)
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


def match_name_version(string):
    regexes = [
        r'^(.*?)\s(\d+\.\d+\s\w+\s\d+\s\(\d+\))',
        r'([\w\s|-].+?)\s(\d\.\d\s\w\d\w)',  # TinkerTool System 8.4 U2B Cracked for macOS
        r'([\w\s|-].+?)\s+v(\d+\.\d+\.\d+\.\d+)',  # ON1 Portrait AI 2023.1 v17.1.1.13620 Cracked for macOS
        r'^(.*?)\s+v?(\d+\.\d+\.\d+\.\d+)',  # Capture One 23 Pro 16.1.1.16 Cracked for macOS
        r'^(.*?)\s+v(\d+\.\d+\.\d+)',  # DVD-Cloner 2022 v9.60.734 Cracked for macOS
        r'^(.*?)\s+v(\d+\.\d+)',  # Adobe Illustrator 2023 v27.0 Cracked for macOS
        r'^([\w\s|-].+?)\s+v?(\d[(\d\w)\.]+(\s\w+\s\d+)?(-[\w].+?)?\s(\([\d\w]+\))?)',
        r'([\w\s|-].+?)\s([\d\.]+\s\([\d]+\))',
        r'(\w+\s\w+)\s(\d+-\d+-\d+)',
        r'(\w+\s\w+\s\w+)\s(\d+\.\d+\.\d+\s\w+)',
    ]

    obj = {
        'name': '',
        'version': ''
    }
    for regex in regexes:
        pattern = re.compile(regex)
        match = pattern.search(string)
        if match:
            obj['name'] = match.group(1)
            obj['version'] = match.group(2)
            return obj
    return obj


def handle_row_data(row_data):
    title = row_data['title']
    obj = match_name_version(title)
    name, version = obj['name'], obj['version']
    description = row_data['description']
    detail_link = row_data['detail_link']
    category_link = row_data['category_link']
    download_link = parse_download_link(row_data)
    db = sqlite.SQLiteDB('haxmac.db')
    app = db.fetchone('SELECT * FROM mac_app WHERE detail_link = ?', [detail_link])
    if app is None:
        db.execute(
            'INSERT INTO mac_app (title, name, latest_version, description, detail_link, category_link, '
            'download_link) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (
                title,
                name,
                version,
                description,
                detail_link,
                category_link,
                download_link
            )
        )

        db.execute(
            'INSERT INTO mac_app_versions (version, detail_link, category_link, download_link, app_id) '
            'VALUES (?, ?, ?, ?, ?)',
            (
                version,
                detail_link,
                category_link,
                download_link,
                db.get_last_rowid()
            )
        )
    elif version != app[3]:
        db.execute(
            'update mac_app set title = ?, name = ?, latest_version = ?, description = ?, detail_link = ?,'
            ' category_link = ?, download_link = ?, update_time = datetime("now", "+8 hours") where id = ?',
            (
                title,
                name,
                version,
                description,
                detail_link,
                category_link,
                download_link,
                app[0]
            )
        )

        db.execute(
            'INSERT INTO mac_app_versions (version, detail_link, category_link, download_link, app_id) '
            'VALUES (?, ?, ?, ?, ?)',
            (
                version,
                detail_link,
                category_link,
                download_link,
                app[0]
            )
        )


def parse_download_link(row_data):
    return ''
