# import json
import utils
import time
from src.utils.tencent_cos import TencentCOS

cos = TencentCOS()
cos.download_file('db/haxmac.db', 'haxmac.db')

# with open('../output/haxmac.json') as f:
#     outputData = json.load(f)
#     utils.handle_list(outputData)
#

page1Data = utils.get_data('https://haxmac.cc/page/1/')

max_page_number = int(page1Data['soup'].select_one('.page-nav.td-pb-padding-side .last').text.strip())

utils.handle_list(page1Data['apps_list'])

for i in range(2, 3):
    wait_time = utils.generate_interval_time()
    time.sleep(wait_time)
    currentPageData = utils.get_data('https://haxmac.cc/page/{0}/'.format(i))
    utils.handle_list(currentPageData['apps_list'])

cos.upload_file('db/haxmac.db', 'haxmac.db')
# with open('haxmac_db.json', 'w') as f:
#     json.dump(apps_list, f)
