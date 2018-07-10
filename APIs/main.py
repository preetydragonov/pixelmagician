import json
import urllib.parse
import urllib.request
import boto3
import io
from PIL import Image

s3 = boto3.client('s3')
bucket = 'searched-words'

def put_images_to_S3(event, context):
    
    queryWord = event['Records'][0]['s3']['object']['key']
    googleImageUrls = google_images_get_html(queryWord)
    
    key = queryWord + ".json"
    body = json.dumps(googleImageUrls)

    try:
        response = s3.put_object(Bucket=bucket, Key=key, Body = body)
        return response
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e

def google_images_get_html(queryWord):
    url = 'https://www.google.com/search?q=' + queryWord + '&espv=2&biw=1366&bih=667&site=webhp&source=lnms&tbm=isch&sa=X&ei=XosDVaCXD8TasATItgE&ved=0CAcQ_AUoAg'

    headers = {}
    headers['User-Agent'] = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"

    request = urllib.request.Request(url, headers = headers)
    response = urllib.request.urlopen(request)
    responseData = str(response.read())

#    newly added 2 lines
#    image_url_list = google_images_get_all_items(responseData)
#    return image_url_list
    image_url_list, pixeled_image_url_list = google_image_get_all_items(responseData)
    return pixeled_image_url_list

def google_images_get_next_item(s):
    start_line = s.find('rg_di')
    if start_line == -1:    #If no links are found then give an error!
        end_quote = 0
        link = "no_links"
        return link, end_quote
    else:
        start_line = s.find('"class="rg_meta"')
        start_content = s.find('"ou"',start_line+1)
        end_content = s.find(',"ow"',start_content+1)
        content_raw = str(s[start_content+6:end_content-1])
        return content_raw, end_content

#Getting all links with the help of '_images_get_next_image'
def google_images_get_all_items(page):
    items = []
    pixeledItems = []
    while True:
        item, end_content = google_images_get_next_item(page)
        if item == "no_links":
            break
        else:
            items.append(item)      #Append all the links in the list named 'Links'
            ##time.sleep(0.1)        #Timer could be used to slow down the request for image downloads
            # newly added two lines below
            pixeledURL = getRandomPixededImageURLFromOriginalImageURL(item)
            pixeledItems.append(pixeledURL)

            page = page[end_content:]
    # newly added pixeled Items
    return items, pixeledItems

#Getting random pixeled image url
def getRandomPixededImageURLFromOriginalImageURL(url):
    #get newImage's random pixel
    requestedImage = urllib.request.urlopen(urllib.request.Request(url)).read()
    requestedImageInByte = Image.open(io.BytesIO(requestedImage))
    pixels = requestedImageInByte.load()
    randomPixel = pixels[random.randint(0, requestedImageInByte.size[0]), random.randint(0, requestedImageInByte.size[1])]

    #get newImage's width and height
    width, height = requestedImageInByte.size
    rate = round(width/height, 2)
    newWidth = 100
    newHeight = int(100 * rate)

    #create newImage with random pixel, width and height
    newImage = Image.new("RGB", (newWidth, newHeight), randomPixel)

    #upload
    stream = io.BytesIO()
    newImage.save(stream, format="png")
    stream.seek(0)
    key = "testFileNew.png"
    s3.put_object(Bucket=bucket, Key=key, Body =stream,ContentType='image/png',ACL='public-read')

    return key

def getRandomPixeledImageFromImageURL(url):
    #get newImage's pixel
    requestedImage = urllib.request.urlopen(urllib.request.Request(url)).read()
    requestedImageInByte = Image.open(io.BytesIO(requestedImage))
    pixels = requestedImageInByte.load()
    randomPixel = pixels[random.randint(0, requestedImageInByte.size[0]), random.randint(0, requestedImageInByte.size[1])]

    #get newImage's width and height
    width, height = requestedImageInByte.size
    rate = round(width/height, 2)
    newWidth = 100
    newHeight = int(100 * rate)

    #create newImage
    newImage = Image.new("RGB", (newWidth, newHeight), randomPixel)

    #upload
    stream = io.BytesIO()
    newImage.save(stream, format="png")
    stream.seek(0)
    key = "testFileNew.png"
    s3.put_object(Bucket=bucket, Key=key, Body =stream,ContentType='image/png',ACL='public-read')

def hello(event, context):
    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response

    # Use this code if you don't use the http event with the LAMBDA-PROXY
    # integration
    """
    return {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "event": event
    }
    """
