from flask import Flask, redirect, request
import macbang_utils as utils
from utils.constants import URL_SEPARATOR
from utils.global_utils import make_no_cache_response
from flask_cors import CORS
from utils.redis_client import RedisClient

app = Flask(__name__)
CORS(app)
app.secret_key = '0c492e83-a301-4df1-8a1b-a4a5e514fb11'
rc = RedisClient()


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/redirect_link')
def redirect_baidu_pan_link():
    rc.delete('record')
    record = utils.get_not_transferred_download_record()
    if record is None:
        return ''
    rc.set_dict('record', record)
    download_link_str = record['data']['download_link']
    download_links = download_link_str.split(URL_SEPARATOR)
    for link in download_links:
        if 'pan.baidu.com' in link:
            return make_no_cache_response(redirect(link))
    return ''


@app.route('/set_transfer_link')
def set_transfer_link():
    url = request.args.get('url')
    record = rc.get_dict('record')
    if url is None or record is None:
        return 'fail'
    utils.set_transfer_link(record['data']['id'], record['type'], url)
    return 'success'


if __name__ == '__main__':
    app.run()
