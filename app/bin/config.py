import ConfigParser
import os
class Config:
    def __init__(self):
        config = ConfigParser.ConfigParser()
        path = os.getcwd() + '/app/config/config.txt';
        config.readfp(open(path))
        self.bucket = config.get('aws','bucket')
        self.apikey = config.get('aws','apikey')
        self.secret = config.get('aws', 'secret')
        self.link = config.get('aws', 'link')
        self.path = config.get('so', 'dir')