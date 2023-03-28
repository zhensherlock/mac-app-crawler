import random
import re
from bs4 import BeautifulSoup
import cloudscraper
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utils.xclient_orm import MacApp, MacAppVersion, MacCategory, MacCategoryApp

engine = create_engine('sqlite:///xclient.db')

Session = sessionmaker(bind=engine)

session = Session()


def generate_interval_time():
    return random.randint(50, 70)


def get_page(url):
    scraper = cloudscraper.create_scraper(delay=10, browser={'custom': 'ScraperBot/1.0', })
    response = scraper.get(url)
    if response.status_code == 200:
        return response.text
    return None


def parse_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    app_blocks = soup.select('.post_list > li')
    apps_list = []
    for app in app_blocks:
        app_title = app.find('h3').text.strip()
        app_desc = app.select_one('p').text.strip()
        app_detail_link = app.find('a')['href']
        category_nodes = app.select('.cates a')
        categories = []
        for category_node in category_nodes:
            category_name = category_node.text.strip()
            category_href = category_node['href']
            categories.append({
                'name': category_name,
                'href': category_href
            })

        app_data = {
            'title': app_title,
            'description': app_desc,
            'detail_link': app_detail_link,
            'categories': categories
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
        r'\] (.+?) [\u4e00-\u9fff]+',
        r'^([\w\s|-].+?)\s+v?(\d[(\d\w)\.]+(\s\w+\s\d+)?(-[\w].+?)?\s(\([\d\w]+\))?)',
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
            obj['version'] = match.group(2) if len(match.groups()) > 1 else '免费'
            return obj
    return obj


def handle_row_data(row_data):
    title = row_data['title']
    obj = match_name_version(title)
    name, version = obj['name'], obj['version']
    description = row_data['description']
    detail_link = row_data['detail_link']
    download_link = parse_download_link(row_data)
    categories = row_data['categories']

    app = session.query(MacApp).filter_by(detail_link=detail_link).first()
    if app is None:
        app = MacApp(title=title, name=name, latest_version=version, description=description,
                     detail_link=detail_link, download_link=download_link)
        session.add(app)
        session.commit()
        mac_app_version = MacAppVersion(version=version, detail_link=detail_link, download_link=download_link,
                                        app_id=app.id)
        session.add(mac_app_version)
        session.commit()
    elif app.latest_version != version:
        app.latest_version = version
        app.description = description
        app.name = name
        app.title = title
        mac_app_version = MacAppVersion(version=version, detail_link=detail_link, download_link=download_link,
                                        app_id=app.id)
        session.add(mac_app_version)
        session.commit()

    for item in categories:
        mac_category = session.query(MacCategory).filter_by(name=item['name']).first()
        if mac_category is None:
            mac_category = MacCategory(name=item['name'])
            session.add(mac_category)
            session.commit()
        if session.query(MacCategoryApp).filter_by(app_id=app.id, category_id=mac_category.id) is None:
            mac_category_app = MacCategoryApp(app_id=app.id, category_id=mac_category.id)
            session.add(mac_category_app)
            session.commit()


def parse_download_link(row_data):
    return ''
