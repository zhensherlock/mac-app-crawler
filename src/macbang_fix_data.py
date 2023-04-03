from utils import tencent
import macbang_utils as utils

cos = tencent.TencentCOS()
cos.download_file('db/macbang.db', 'macbang.db')

utils.fix_data()

cos.upload_file('db/macbang.db', 'macbang.db')
