# from utils import tencent
import re
import macbang_utils as utils

# cos = tencent.TencentCOS()
# cos.download_file('db/macbang.db', 'macbang.db')


page1Data = utils.get_data('https://macbang.net/page/1/')

max_page_number_url = page1Data['soup'].select_one('.pagination a:last-child')['href']
max_page_number_match = re.search(r'\d+', max_page_number_url)
max_page_number = 100

if max_page_number_match:
    max_page_number = int(max_page_number_match.group(0))

utils.handle_list(page1Data['apps_list'])

# for i in range(2, max_page_number + 1):
#     wait_time = utils.generate_interval_time()
#     time.sleep(wait_time)
#     currentPageData = utils.get_data('https://macbang.net/page/{0}/'.format(i))
#     utils.handle_list(currentPageData['apps_list'])

# cos.upload_file('db/macbang.db', 'macbang.db')
