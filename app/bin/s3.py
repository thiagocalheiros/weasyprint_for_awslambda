import boto3
from app.bin.config import Config

class S3:
    def __init__(self):
        self.config = Config()

    def send(self, filePath, name):
        boto3.resource(
            's3',
            aws_access_key_id=self.config.apikey,
            aws_secret_access_key=self.config.secret
        ).Object(
            self.config.bucket
        ).upload_file(filePath)
        return self.config.link.format(self.config.bucket, name)