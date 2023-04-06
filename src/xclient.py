import time
from utils import tencent
import xclient_utils as utils
from utils.global_utils import generate_interval_time, get_tag_name, get_page_range

cos = tencent.TencentCOS()
cos.retry_download_file('db/xclient.db', 'xclient.db')

page_range = get_page_range(get_tag_name())
if page_range is None:
    page_range = {
        'start': 1,
        'end': None
    }

page1Data = utils.get_data('https://xclient.info/s/{0}/'.format(page_range['start']))

if page_range['end'] is None:
    page_range['end'] = int(page1Data['soup'].select_one('.page-navigator li:nth-last-child(2)').text.strip())

utils.handle_list(page1Data['apps_list'])

for i in range(2, page_range['end'] + 1):
    wait_time = generate_interval_time()
    time.sleep(wait_time)
    currentPageData = utils.get_data('https://xclient.info/s/{0}/'.format(i))
    utils.handle_list(currentPageData['apps_list'])

cos.retry_upload_file('db/xclient.db', 'xclient.db')
