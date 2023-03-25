# import json
import time
from utils import tencent
import haxmac_utils as utils

cos = tencent.TencentCOS()
cos.download_file('db/haxmac.db', 'haxmac.db')

# with open('../output/haxmac.json') as f:
#     outputData = json.load(f)

page1Data = utils.get_data('https://haxmac.cc/page/1/')

max_page_number = int(page1Data['soup'].select_one('.page-nav.td-pb-padding-side .last').text.strip())

utils.handle_list(page1Data['apps_list'])

for i in range(2, max_page_number + 1):
    wait_time = utils.generate_interval_time()
    time.sleep(wait_time)
    currentPageData = utils.get_data('https://haxmac.cc/page/{0}/'.format(i))
    utils.handle_list(currentPageData['apps_list'])

cos.upload_file('db/haxmac.db', 'haxmac.db')
# with open('haxmac_db.json', 'w') as f:
#     json.dump(apps_list, f)
