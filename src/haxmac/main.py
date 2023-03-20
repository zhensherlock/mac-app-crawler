import json
import utils
import time


# with open('../output/apps.json') as f:
#     outputData = json.load(f)

# with open('../assets/apps.json') as f:
#     data = json.load(f)
#
# print(data)

page1Data = utils.get_data('https://haxmac.cc/page/1/')

max_page_number = int(page1Data['soup'].select_one('.page-nav.td-pb-padding-side .last').text.strip())

apps_list = page1Data['apps_list']

for i in range(1, max_page_number):
    wait_time = utils.generate_interval_time()
    time.sleep(wait_time)
    currentPageData = utils.get_data('https://haxmac.cc/page/{0}/'.format(i))
    apps_list.extend(currentPageData['apps_list'])


with open('../output/haxmac.json', 'w') as f:
    json.dump(apps_list, f)

