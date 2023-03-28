import time
from utils import tencent
import xclient_utils as utils

cos = tencent.TencentCOS()
cos.download_file('db/xclient.db', 'xclient.db')


page1Data = utils.get_data('https://xclient.info/s/1/')

max_page_number = int(page1Data['soup'].select_one('.page-navigator li:nth-last-child(2)').text.strip())

utils.handle_list(page1Data['apps_list'])

for i in range(2, max_page_number + 1):
    wait_time = utils.generate_interval_time()
    time.sleep(wait_time)
    currentPageData = utils.get_data('https://xclient.info/s/{0}/'.format(i))
    utils.handle_list(currentPageData['apps_list'])

cos.upload_file('db/xclient.db', 'xclient.db')
