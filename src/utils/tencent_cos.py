import os
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client


class TencentCOS:
    def __init__(self, secret_id=os.environ['secret_id'], secret_key=os.environ['secret_key'],
                 region=os.environ['cos_region'], bucket=os.environ['cos_bucket']):
        self.secret_id = secret_id
        self.secret_key = secret_key
        self.region = region
        self.bucket = bucket
        self.token = None
        self.scheme = 'https'
        self.config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=self.token,
                                Scheme=self.scheme)
        self.client = CosS3Client(self.config)

    def download_file(self, cos_path, local_path):
        response = self.client.get_object(
            Bucket=self.bucket,
            Key=cos_path,
        )
        response['Body'].get_stream_to_file(local_path)

    def upload_file(self, cos_path, local_path):
        self.client.upload_file(
            Bucket=self.bucket,
            LocalFilePath=local_path,
            Key=cos_path,
            PartSize=1,
            MAXThread=10,
            EnableMD5=False
        )
        # print(response['ETag'])
