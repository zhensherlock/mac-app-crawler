import os
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client


def download_obj(remote_file, local_file):
    secret_id = os.environ['secret_id']
    secret_key = os.environ['secret_key']
    region = os.environ['cos_bucket']
    bucket = os.environ['cos_region']
    token = None
    scheme = 'https'

    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)
    client = CosS3Client(config)
    response = client.get_object(
        Bucket=bucket,
        Key=remote_file,
    )
    response['Body'].get_stream_to_file(local_file)

def upload_cloud():
    secret_id = os.environ['secret_id']
    secret_key = os.environ['secret_key']
    region = os.environ['cos_bucket']
    bucket = os.environ['cos_region']
    token = None
    scheme = 'https'

    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)
    client = CosS3Client(config)
    response = client.upload_file(
        Bucket=bucket,
        LocalFilePath='local.txt',
        Key='picture.jpg',
        PartSize=1,
        MAXThread=10,
        EnableMD5=False
    )
    print(response['ETag'])
