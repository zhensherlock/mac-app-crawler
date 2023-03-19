import requests
from bs4 import BeautifulSoup


def get_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
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
