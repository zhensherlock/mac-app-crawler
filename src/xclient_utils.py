import re
import time
from datetime import datetime
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utils.constants import URL_SEPARATOR, IMAGE_SEPARATOR
from utils.global_utils import get_page, generate_interval_time
from utils.xclient_orm import MacApp, MacAppVersion, MacCategory, MacCategoryApp, MacTag, MacAppTag

engine = create_engine('sqlite:///xclient.db')

Session = sessionmaker(bind=engine)

session = Session()


def parse_list_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    app_nodes = soup.select('.post_list > li:first-child')
    apps_list = []
    for app in app_nodes:
        app_title = app.find('h3').text.strip()
        app_desc = app.select_one('p').text.strip()
        app_detail_link = app.find('a')['href']
        category_nodes = app.select('.cates a')

        app_data = {
            'title': app_title,
            'description': app_desc,
            'detail_link': app_detail_link,
            'categories': []
        }
        for category_node in category_nodes:
            category_name = category_node.text.strip()
            category_href = category_node['href']
            app_data['categories'].append({
                'name': category_name,
                'href': category_href
            })

        wait_time = generate_interval_time(5, 10)
        time.sleep(wait_time)
        detail_page_html = get_page(app_detail_link)
        if detail_page_html:
            detail_data = parse_detail_page(detail_page_html, app_detail_link)
            app_data['latest_version'] = detail_data['latest_version']
            app_data['versions'] = detail_data['versions']
            app_data['logo'] = detail_data['logo']
            app_data['thumbnail'] = detail_data['thumbnail']
            app_data['content'] = detail_data['content']
            app_data['view_count'] = detail_data['view_count']
            app_data['download_count'] = detail_data['download_count']
            app_data['update_time'] = detail_data['update_time']
            app_data['tags'] = detail_data['tags']

        apps_list.append(app_data)

    return {
        'soup': soup,
        'apps_list': apps_list
    }


def parse_detail_page(html, link):
    soup = BeautifulSoup(html, 'html.parser')
    logo = soup.select_one('.app_ico')['src']
    title = soup.select_one('.post-title').text.strip()
    update_time = soup.select_one('.post-meta li:nth-child(1)').text.strip()
    tag_nodes = soup.select('.post-meta li:nth-child(2) a')
    content_node = soup.select_one('#post-content')
    latest_version = soup.select_one('.app_info tr:nth-of-type(1) td').text.strip()
    tags = []
    for tag_node in tag_nodes:
        category_name = tag_node.text.strip()
        category_href = tag_node['href']
        tags.append({
            'name': category_name,
            'href': category_href
        })
    view_count = soup.select_one('.post-meta li:nth-child(3)').text.strip()
    thumbnails = []
    thumbnail_nodes = soup.select('#swiper-wrapper img')
    for thumbnail_node in thumbnail_nodes:
        thumbnails.append(thumbnail_node['src'])
    download_count_node = soup.select_one('.downloads')
    download_count_title_node = download_count_node.find('span')
    if download_count_title_node:
        download_count_title_node.extract()
    download_count = download_count_node.text.strip()
    versions = []
    version_nodes = soup.select('#versions tbody tr')
    for version_node in version_nodes:
        download_nodes = version_node.select('td:nth-child(5) a')
        download_links = []
        for download_node in download_nodes:
            wait_time = generate_interval_time(1, 3)
            time.sleep(wait_time)
            download_page_html = get_page(download_node['href'], headers={'referer': link})
            if download_page_html:
                download_links.append(parse_download_page(download_page_html))
        versions.append({
            'version': version_node.select_one('td:nth-child(1)').text.strip(),
            'language': version_node.select_one('td:nth-child(2)').text.strip(),
            'post_time': version_node.select_one('td:nth-child(3)').text.strip(),
            'size': version_node.select_one('td:nth-child(4)').text.strip(),
            'download_link': URL_SEPARATOR.join(download_links)
        })
    return {
        'logo': logo,
        'update_time': update_time,
        'view_count': view_count,
        'tags': tags,
        'thumbnail': IMAGE_SEPARATOR.join(thumbnails),
        'download_count': download_count,
        'content': content_node.prettify(),
        'latest_version': latest_version,
        'versions': versions
    }


def parse_download_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    download_node = soup.select_one('.down_wrap a')
    download_type = download_node.text.strip()
    download_href = download_node['href']
    download_link = download_node['data-link'] if download_node.has_attr('data-link') else ''
    download_password = download_node['data-clipboard-text'] if download_node.has_attr('data-clipboard-text') else ''
    ctwp_password_parameter = '?p={0}'.format(download_password)
    baidu_password_parameter = '?pwd=${0}'.format(download_password)
    if 'http' in download_href:
        return download_href
    if '城通网盘下载' in download_type and ctwp_password_parameter in download_link:
        return download_link
    if '城通网盘下载' in download_type and not(ctwp_password_parameter in download_link):
        return '${0}?p=${1}'.format(download_link, download_password)
    if '百度云盘下载' in download_type and baidu_password_parameter in download_link:
        return download_link
    if '百度云盘下载' in download_type and not(baidu_password_parameter in download_link):
        return '${0}?pwd=${1}'.format(download_link, download_password)


def get_data(url):
    html = get_page(url)
    if html is None:
        return None
    data = parse_list_page(html)

    return {
        'soup': data['soup'],
        'apps_list': data['apps_list']
    }


def handle_list(data):
    for row in data:
        handle_row_data(row)


def match_name_version_slogan(row_data):
    regexes = [
        r"(.+?)\sv?(\d[(\d\w)\.]+[a-zA-Z\d]+(\s?\[\w+\])?(\s[Dev|fixed|beta][a-zA-Z]+[(\d\w)\s]+[a-zA-Z\d])?(\s\(["
        r"\d\w]+\))?)(.+)",
    ]

    obj = {
        'name': None,
        'version': None,
        'slogan': None
    }
    title = row_data['title'] + ' '
    latest_version = row_data['latest_version']
    if latest_version in title:
        split_result = title.split(latest_version)
        obj['name'] = split_result[0].strip()
        obj['version'] = latest_version
        obj['slogan'] = split_result[1].strip()
        return obj
    if '免费精品' in title:
        matches = re.search(r'\[免费精品\] (.+?) [\u4e00-\u9fff]+', title)
        if matches:
            obj['name'] = matches.group(1)
            obj['version'] = '官网'
            split_name_result = title.split(obj['name'])
            if split_name_result:
                obj['slogan'] = split_name_result[1].strip()
    else:
        for regex in regexes:
            pattern = re.compile(regex)
            matches = pattern.search(title)
            if matches:
                matches_groups = matches.groups()
                obj['name'] = matches.group(1)
                obj['version'] = matches.group(2)
                obj['slogan'] = matches.group(len(matches_groups)).strip()
    return obj


def handle_row_data(row_data):
    title = row_data['title']
    obj = match_name_version_slogan(row_data)
    name, version, slogan = obj['name'], obj['version'], obj['slogan']
    description = row_data['description']
    detail_link = row_data['detail_link']
    logo = row_data['logo']
    thumbnail = row_data['thumbnail']
    content = row_data['content']
    view_count = row_data['view_count']
    download_count = row_data['download_count']
    update_time = datetime.strptime(row_data['update_time'], '%Y-%m-%d %H:%M:%S')
    categories = row_data['categories']
    versions = row_data['versions']
    tags = row_data['tags']

    app = session.query(MacApp).filter_by(detail_link=detail_link).first()
    if app is None:
        app = MacApp(title=title, name=name, latest_version=version, description=description, content=content,
                     detail_link=detail_link, logo=logo, thumbnail=thumbnail, view_count=view_count,
                     download_count=download_count, update_time=update_time, slogan=slogan)
        session.add(app)
        session.commit()
    elif app.latest_version != version:
        app.latest_version = version
        app.update_time = update_time

    for item in categories:
        mac_category = session.query(MacCategory).filter_by(name=item['name']).first()
        if mac_category is None:
            mac_category = MacCategory(name=item['name'], link=item['href'])
            session.add(mac_category)
            session.commit()
        if session.query(MacCategoryApp).filter_by(app_id=app.id, category_id=mac_category.id).first() is None:
            mac_category_app = MacCategoryApp(app_id=app.id, category_id=mac_category.id)
            session.add(mac_category_app)
            session.commit()

    for item in tags:
        mac_tag = session.query(MacTag).filter_by(name=item['name']).first()
        if mac_tag is None:
            mac_tag = MacTag(name=item['name'], link=item['href'])
            session.add(mac_tag)
            session.commit()
        if session.query(MacAppTag).filter_by(app_id=app.id, tag_id=mac_tag.id).first() is None:
            mac_app_tag = MacAppTag(app_id=app.id, tag_id=mac_tag.id)
            session.add(mac_app_tag)
            session.commit()

    for item in versions:
        mac_app_version = session.query(MacAppVersion).filter_by(app_id=app.id, version=item['version']).first()
        if mac_app_version is None:
            mac_app_version = MacAppVersion(app_id=app.id, version=item['version'], language=item['language'],
                                            post_time=datetime.strptime(item['post_time'], '%Y-%m-%d'),
                                            download_link=item['download_link'], size=item['size'])
            session.add(mac_app_version)
            session.commit()
