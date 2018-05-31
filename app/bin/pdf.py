import json
import base64
import time
import os
from app.bin.config import Config
from weasyprint import HTML


class pdf:
    path = ''
    name = ''
    html = ''
    file = ''
    filePath = ''

    def __init__(self):
        self.path = Config().path

    def fromHTML(self, event):
        o = json.loads(json.dumps(event))
        self.html = base64.b64decode(o.get('html'))
        self.name = str(time.time()) + '-' + o.get('name')
        self.filePath = self.path + self.name

        html = HTML(string = self.html)
        html.write_pdf(self.filePath)

        return self

    def remove(self):
        return os.remove(self.filePath)
