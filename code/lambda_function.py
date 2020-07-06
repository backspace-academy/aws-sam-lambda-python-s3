import boto3
import os
import sys
import uuid
from urllib.parse import unquote_plus
from PIL import Image
import PIL.Image

s3_client = boto3.client('s3')

# Resize image to 200 width maintaining aspect ratio
def resize_image(image_path, resized_path):
    with Image.open(image_path) as image:
        print('Resizing image...')
        width = 200
        wpercent = (width / float(image.size[0]))
        hsize = int((float(image.size[1]) * float(wpercent)))
        image = image.resize((width, hsize), PIL.Image.ANTIALIAS)
        image.save(resized_path)

def lambda_handler(event, context):
    print('Function loaded successfully')    
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    # Object key may have spaces or unicode non-ASCII characters.
    tmpkey = unquote_plus(key.replace('/', ''))
    # Download and store image in Lambda temporary storage
    print('Downloading source image from S3...')
    download_path = '/tmp/{}{}'.format(uuid.uuid4(), tmpkey)
    s3_client.download_file(bucket, key, download_path)
    # Resize image and store in Lambda temporary storage    
    upload_path = '/tmp/resized-{}'.format(tmpkey)    
    resize_image(download_path, upload_path)
    # Upload resized image to S3
    print('Uploading resized image to S3...')    
    s3_client.upload_file(upload_path, '{}-resized'.format(bucket), key)
