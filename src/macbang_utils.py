import re
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utils.constants import URL_SEPARATOR
from utils.global_utils import get_page, generate_interval_time
from utils.macbang_orm import MacApp, MacAppVersions, MacCategory, MacCategoryApps, MacArticle, MacTag, MacArticleTags

engine = create_engine('sqlite:///macbang.db')

Session = sessionmaker(bind=engine)

session = Session()


def parse_list_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    article_nodes = soup.select('article')
    article_list = []
    for article in article_nodes:
        article_title = article.select_one('.type-list-title').text.strip()
        article_datetime = article.select_one('.type-list-date').text.strip()
        article_desc = article.select_one('.type-list-excerpt').text
        article_thumbnail = article.select_one('.wp-post-image')
        article_detail_link = article.select_one('.type-list-title a')['href']
        category_nodes = article.select('.type-list-meta a[rel="category tag"]')
        categories = []
        for category_node in category_nodes:
            category_name = category_node.text.strip()
            category_href = category_node['href']
            categories.append({
                'name': category_name,
                'href': category_href
            })
        article_data = {
            'title': article_title,
            'datetime': article_datetime,
            'description': article_desc,
            'detail_link': article_detail_link,
            'categories': categories,
            'tags': [],
            'thumbnail': '',
            'content': '',
            'link': '',
            'web_post_id': ''
        }
        if article_thumbnail:
            article_data['thumbnail'] = article_thumbnail['src']
        wait_time = generate_interval_time(5, 10)
        time.sleep(wait_time)
        detail_page_html = get_page(article_detail_link)
        if detail_page_html:
            detail_data = parse_detail_page(detail_page_html)
            article_data['content'] = detail_data['content']
            article_data['link'] = detail_data['link']
            article_data['web_post_id'] = detail_data['id']
            article_data['tags'] = detail_data['tags']

        article_list.append(article_data)

    return {
        'soup': soup,
        'apps_list': article_list
    }


def parse_detail_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    article_node = soup.select_one('article')
    article_id = 0
    article_id_match = re.search(r'\d+', article_node['id'])
    if article_id_match:
        article_id = article_id_match.group()
    tag_nodes = soup.select('.post-tags a[rel="tag"]')
    tags = []
    for tag_node in tag_nodes:
        tag_name = tag_node.text.strip()
        tag_href = tag_node['href']
        tags.append({
            'name': tag_name,
            'href': tag_href
        })
    content_node = soup.select_one('.entry.themeform')
    article_download_links = []
    for download_button in content_node.select('.dlipp-dl-btn.j-wbdlbtn-dlipp'):
        article_download_links.append(get_download_link(article_id, download_button['data-rid']))
    for remove_node in content_node.find_all(class_=['dlipp-cont-wp', 'wbp-cbm', 'clear']):
        remove_node.extract()
    return {
        'id': article_id,
        'content': content_node.prettify(),
        'link': URL_SEPARATOR.join(article_download_links),
        'tags': tags
    }


def get_download_link(article_id, download_type):
    url = 'https://macbang.net/wp-admin/admin-ajax.php'
    headers = {
        'authority': 'macbang.net',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'no-cache',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'cookie': 'Hm_lvt_f7958d48dde5d65b4e2a458c87e7c6c7=1680017015; '
                  '__gads=ID=1a3ee13365ae4e65-22b2d877c3dc0043:T=1680017015:RT=1680017015:S'
                  '=ALNI_MbbTAyZcNJ8tFl53AgGCTpfVNkeBA; '
                  '__gpi=UID=00000be5734efb5c:T=1680017015:RT=1680052832:S=ALNI_MaDVegLL3WrUJhmxtPNpnSq2xxWMA; '
                  'Hm_lpvt_f7958d48dde5d65b4e2a458c87e7c6c7=1680070261',
        'origin': 'https://macbang.net',
        'pragma': 'no-cache',
        'referer': 'https://macbang.net/topaz-video-ai-for-mac-v3-1-7.html',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/111.0.0.0 Safari/537.36'
    }
    data = {
        'action': 'wb_dlipp_front',
        'pid': article_id,
        'rid': download_type
    }
    response = requests.post(url, headers=headers, data=data)
    url = ''
    if response.status_code == 200:
        res_json = response.json()
        pwd = res_json['data']['pwd']
        url = res_json['data']['url']
        if download_type == 'baidu' and not ('pwd=' in url):
            url += '?pwd=' + pwd
    return url


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


def match_name_version_slogan(string):
    regexes = [
        r"(.+?)\sv?(\d[(\d\w)\.]+[a-zA-Z\d]+(\s?\[\w+\])?(\s[Dev|fixed|beta][a-zA-Z]+[(\d\w)\s]+[a-zA-Z\d])?(\s\(["
        r"\d\w]+\))?)(.+)",
    ]

    obj = {
        'name': None,
        'version': None,
        'slogan': None
    }
    for regex in regexes:
        pattern = re.compile(regex)
        match = pattern.search(string)
        if match:
            match_groups = match.groups()
            obj['name'] = match.group(1)
            obj['version'] = match.group(2)
            obj['slogan'] = match.group(len(match_groups)).strip()
            return obj
    return obj


def handle_row_data(row_data):
    title = row_data['title']
    obj = match_name_version_slogan(title)
    name, version, slogan = obj['name'], obj['version'], obj['slogan']
    description = row_data['description']
    post_datetime = datetime.strptime(row_data['datetime'], '%Y年%m月%d日')
    thumbnail = row_data['thumbnail']
    detail_link = row_data['detail_link']
    download_link = row_data['link']
    content = row_data['content']
    categories = row_data['categories']
    tags = row_data['tags']
    web_post_id = row_data['web_post_id']

    mac_category = None
    for item in categories:
        mac_category = session.query(MacCategory).filter_by(name=item['name']).first()
        if mac_category is None:
            mac_category = MacCategory(name=item['name'])
            session.add(mac_category)
            session.commit()

    article = session.query(MacArticle).filter_by(detail_link=detail_link).first()
    if article is None:
        article = MacArticle(title=title, description=description, content=content, thumbnail=thumbnail,
                             detail_link=detail_link, download_link=download_link, category_id=mac_category.id,
                             web_post_id=web_post_id, web_post_time=post_datetime)
        session.add(article)
        session.commit()
    if name is None:
        return
    app = session.query(MacApp).filter_by(name=name).first()
    if app is None:
        app = MacApp(title=title, name=name, latest_version=version, description=description, slogan=slogan,
                     content=content, detail_link=detail_link, download_link=download_link)
        session.add(app)
        session.commit()
        mac_app_version = MacAppVersions(version=version, detail_link=detail_link, download_link=download_link,
                                         app_id=app.id, web_post_time=post_datetime, article_id=article.id)
        session.add(mac_app_version)
        session.commit()
    elif app.latest_version != version:
        mac_app_version = MacAppVersions(version=version, detail_link=detail_link, download_link=download_link,
                                         app_id=app.id, web_post_time=post_datetime, article_id=article.id)
        session.add(mac_app_version)
        session.commit()

    if session.query(MacCategoryApps).filter_by(app_id=app.id, category_id=mac_category.id).first() is None:
        mac_category_app = MacCategoryApps(app_id=app.id, category_id=mac_category.id)
        session.add(mac_category_app)
        session.commit()

    for item in tags:
        mac_tag = session.query(MacTag).filter_by(title=item['name']).first()
        if mac_tag is None:
            mac_tag = MacTag(title=item['name'], link=item['href'])
            session.add(mac_tag)
            session.commit()
        if session.query(MacArticleTags).filter_by(article_id=article.id, tag_id=mac_tag.id).first() is None:
            mac_article_tag = MacArticleTags(article_id=article.id, tag_id=mac_tag.id)
            session.add(mac_article_tag)
            session.commit()


def fix_prod_data():
    apps = session.query(MacApp).all()
    for app in apps:
        detail_page_html = get_page(app.detail_link)
        if detail_page_html:
            detail_data = parse_detail_page(detail_page_html)
            link = detail_data['link']
            app.description = app.description.strip()
            if link is not None and link != '' and app.download_link != link:
                app.download_link = link
        wait_time = generate_interval_time(3, 5)
        time.sleep(wait_time)

    # app_versions = session.query(MacAppVersions).all()
    # for app_version in app_versions:
    #     detail_page_html = get_page(app_version.detail_link)
    #     if detail_page_html:
    #         detail_data = parse_detail_page(detail_page_html)
    #         link = detail_data['link']
    #         if link is not None and link != '' and app_version.download_link != link:
    #             app_version.download_link = link
    #     wait_time = generate_interval_time(3, 5)
    #     time.sleep(wait_time)
    session.commit()
