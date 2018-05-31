from app.bin.pdf import pdf
from app.bin.s3 import S3

def lambda_handler(event, context):
    o = pdf().fromHTML(event)
    link = S3().send(o.filePath, o.name)
    o.remove()
    return link