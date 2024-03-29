# -*-encoding: utf-8 -*-
import json
import urllib.parse
from urllib.error import HTTPError
import urllib.request
import boto3
from botocore.errorfactory import ClientError
import random
import io
from PIL import Image
import ssl
from icrawler.builtin import GoogleImageCrawler
import os

s3 = boto3.client('s3')
bucket = 'searched-words'
Lambda = boto3.client('lambda')

#The API
def put_pixels_to_s3(event, context):
    try:
        image_url = getTargetValueFromEvent(target="image_url", event=event)
    except Exception as exception:
        print("Cannot get value of key 'image_url' from event.")
        raise exception
    try:
        response = getResponse(image_url)
    except Exception as exception:
        print("Cannot get response from Given URL.")
        raise exception
    try:
        requested_image = response.read()
    except Exception as exception:
        print("Cannot read response.")
        raise exception
    try:
        pixeled_image_stream = getRandomPixeledImageFromOriginalImageURL(requested_image)
    except Exception as exception:
        print("Cannot get random pixeled image.")
        raise exception
    try:
        key = create_key_for_pixeled_image(image_url)
        s3.put_object(Bucket=bucket,
                      Key=key,
                      Body=pixeled_image_stream,
                      ContentType='image/jpg',
                      ACL='public-read')
    except Exception as exception:
        print("Cannot put object To S3.")
        raise exception


def put_images_to_s3_by_using_icrawler(event, context):
    try:
        query_word = getTargetValueFromEvent(target="query_word", event=event)
    except Exception as exception:
        print("Cannot get value of key 'query_word' from event.")
        raise exception
    try:
        date_range = getTargetValueFromEvent(target="date_range", event=event)
        date_range_in_tuple = (tuple(date_range[0]), tuple(date_range[1]))
    except Exception as exception:
        print("Cannot get value of key 'dataRange' from event.")
        raise exception
    try:
        max_iteration = getTargetValueFromEvent(target="max_iteration", event=event)
    except Exception as exception:
        print("Cannot get value of key 'max_iteration' from event.")
        raise exception

    directory = (
        'images/' + query_word + "/" +
        'original' + '/' +
        str(date_range_in_tuple[0][0]) + '_' + str(date_range_in_tuple[0][1]) + '_' + str(date_range_in_tuple[0][2]) +
        "-" +
        str(date_range_in_tuple[1][0]) + '_' + str(date_range_in_tuple[1][1]) + '_' + str(date_range_in_tuple[1][2])
    )

    try:
        s3.head_object(Bucket=bucket, Key='icrawler/' + directory + '/000001.jpg')
        print(query_word + " exists! so I will stop here.")
        return
    except ClientError:
        pass

    google_crawler = GoogleImageCrawler(
        downloader_threads=1,
        storage={'root_dir': '/tmp/' + directory})
    google_crawler.crawl(query_word, filters=dict(date=date_range_in_tuple), max_num=max_iteration)

    print("crawl ended")
    print(os.path.isfile('/tmp/' + directory + '/000001.jpg'))

    with open('/tmp/' + directory + '/000001.jpg', 'w') as f:
        print(f)
        print("read 000001.jpg from memory: success!")

    # todo 파일 경로를 저장하는 리스트
    # todo 해당 파일 경로가 존재하는 경우에, 저장될 주소를 따로 저장하도록 한다.

    for i in list(range(1, 5)):
        file_path = '/tmp/' + directory + '/00000{}.jpg'.format(i)
        key = 'icrawler/' + directory + '/' + '00000{}.jpg'.format(i)
        try:
            s3.upload_file(file_path, Bucket=bucket, Key=key, ExtraArgs={'ACL':'public-read'})
            print("uploaded file to S3")
        except Exception as exception:
            print('Error getting object {} from bucket {}.'.format(key, bucket))
            raise exception

        image_url = "https://s3.ap-northeast-2.amazonaws.com/searched-words/" + key
        payload = addDataToPayloadFormat(data={"image_url": image_url})
        
        try:
            Lambda.invoke(FunctionName="APIs-dev-put_pixels_to_s3",
                          InvocationType='Event',
                          Payload=json.dumps(payload))
            print("triggered pixel uploading function")
        except Exception as exception:
            raise exception

    # todo 파일 경로 리스트를 올려주는 함수


def icrawler_trigger(event, context):
    try:
        query_word = getTargetValueFromEvent(target="query_word", event=event)
    except Exception as exception:
        print("Cannot get value of key 'query_word' from event.")
        raise exception

    for date_range in createDateRangeList(yearRange=7):
        payload = addDataToPayloadFormat(data={"query_word": query_word,
                                               "date_range": date_range,
                                               "max_iteration": 4})
        Lambda.invoke(FunctionName="APIs-dev-put_images_to_s3_by_using_icrawler",
                      InvocationType='Event',
                      Payload=json.dumps(payload))


def put_images_to_S3(event, context):
    queryWord = event['Records'][0]['s3']['object']['key']
    googleImageUrls = google_images_get_html(queryWord)

    key = queryWord + ".json"
    body = json.dumps(googleImageUrls)

    try:
        response = s3.put_object(Bucket=bucket, Key=key, Body=body)
        return response
    except Exception as e:
        print(e)
        print(
            'Error getting object {} from bucket {}.'.format(key, bucket))
        raise e


def google_images_get_html(queryWord):
    url = 'https://www.google.com/search?q=' + queryWord + '&espv=2&biw=1366&bih=667&site=webhp&source=lnms&tbm=isch&sa=X&ei=XosDVaCXD8TasATItgE&ved=0CAcQ_AUoAg'

    headers = {}
    headers[
        'User-Agent'] = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"

    request = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(request)
    responseData = str(response.read())

    #    newly added 2 lines
    #    image_url_listders = {} = google_images_get_all_items(responseData)
    #    return image_url_list
    image_url_list, pixeled_image_url_list = google_images_get_all_items(responseData)
    return image_url_list


def google_images_get_next_item(s):
    start_line = s.find('rg_di')
    if start_line == -1:  # If no links are found then give an errorponse = urllib.request.urlopen(request, context=context)
        end_quote = 0
        link = "no_links"
        return link, end_quote
    else:
        start_line = s.find('"class="rg_meta"')
        start_content = s.find('"ou"', start_line + 1)
        end_content = s.find(',"ow"', start_content + 1)
        content_raw = str(s[start_content + 6:end_content - 1])
        return content_raw, end_content


# check PIL supporting image format
def checkIfImageFormatIsSupportedByPIL(imageFormat):
    return imageFormat in ('image/png', 'image/jpeg', 'image/gif')


def getImageFormat(response):
    return response.headers['Content-Type'].split(';')[0].lower()


def readResponse(response):
    return response.read()

# Used
# Getting url request page
def getResponse(url):
    context = ssl._create_unverified_context()
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"}
    try:
        request = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(request, context=context)
        return response
    except HTTPError as httpError:
        print("error while opening url")
        print("the error url is " + url)
        raise httpError


# Getting all links with the help of '_images_get_next_image'
def google_images_get_all_items(page):
    originalUrls = []
    pixeledUrls = []
    while True:
        originalUrl, end_content = google_images_get_next_item(page)
        if originalUrl == "no_links":
            break
        else:
            try:
                response = getResponse(originalUrl)
                imageFormat = getImageFormat(response)
                #                print(imageFormat)
                if (checkIfImageFormatIsSupportedByPIL(imageFormat)):
                    print(originalUrl)
            #                    originalUrls.append(originalUrl)      #Append all the links in the list named 'Links'
            #                    ##time.sleep(0.1)        #Timer could be used to slow down the request for image downloads
            #                    # newly added two lines below
            #                    requestedImage = response.read()
            #                    pixeledUrl = getRandomPixeledImageURLFromOriginalImageURL(requestedImage)
            #                    pixeledUrls.append(pixeledUrl)
            except:
                print("ERROR!")
                print("handled!")
                print("going to next")
            page = page[end_content:]

    # newly added pixeled Items
    return originalUrls, pixeledUrls


# Getting random pixeled image url
def getRandomPixeledImageURLFromOriginalImageURL(requestedImage):
    # get newImage's random pixel
    # This restores the same behavior as before.
    #    context = ssl._create_unverified_context()
    #    headers = {}
    #    headers['User-Agent'] = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"
    #    req = urllib.request.Request(url, headers = headers)
    #    requestedImage = urllib.request.urlopen(req, context=context).read()
    imageInBytes = io.BytesIO(requestedImage)
    requestedImageInByte = Image.open(imageInBytes)
    pixels = requestedImageInByte.load()
    width, height = requestedImageInByte.size
    randomPixel = pixels[random.randint(0, width), random.randint(0, height)]

    if not isinstance(randomPixel, tuple):
        randomPixel = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    if len(randomPixel) < 3:
        randomPixel = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    # get newImage's width and height
    width, height = requestedImageInByte.size
    rate = round(width / height, 2)
    newWidth = 100
    newHeight = int(100 * rate)

    print(newWidth, newHeight, randomPixel)
    # create newImage with random pixel, width and height
    newImage = Image.new("RGB", (newWidth, newHeight), randomPixel)

    key = 'out'
    newImage.save('./out.jpg')
    # upload
    #    stream = io.BytesIO()
    #    newImage.save(stream, format="png")
    #    stream.seek(0)
    #    key = "testFileNew.png"
    #    s3.put_object(Bucket=bucket, Key=key, Body =stream,ContentType='image/png',ACL='public-read')
    #
    return key

#Used
def getRandomPixeledImageFromOriginalImageURL(requested_image):
    opened_image = openImage(requested_image)
    random_pixel = getRandomPixel(opened_image)
    if not isinstance(random_pixel, tuple):
        random_pixel = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    if len(random_pixel) < 3:
        random_pixel = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    stream = io.BytesIO()
    pixeled_image = createPixeledImageInSmallerSize(opened_image, random_pixel)
    pixeled_image.save(stream, format="jpeg")
    stream.seek(0)
    return stream


def openImage(image):
    imageInBytes = io.BytesIO(image)
    return Image.open(imageInBytes)

#Used
def getRandomPixel(imageInByte):
    pixels = imageInByte.load()
    width, height = imageInByte.size
    randomPixel = pixels[random.randint(0, width), random.randint(0, height)]
    return randomPixel

#Used
def createPixeledImageInSmallerSize(imageInByte, randomPixel):
    width, height = imageInByte.size
    rate = round(width / height, 2)
    newWidth = 100
    newHeight = int(100 * rate)
    return Image.new("RGB", (newWidth, newHeight), randomPixel)


# def getRandomPixeledImageFromImageURL(url):
# get newImage's pixel
#    headers = {}
#    headers['User-Agent'] = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"
#    req = urllib.request.Request(url, headers = headers)
#    requestedImage = urllib.request.urlopen(req).read()
#    requestedImageInByte = Image.open(io.BytesIO(requestedImage))
#    pixels = requestedImageInByte.load()
#    randomPixel = pixels[random.randint(0, requestedImageInByte.size[0]), random.randint(0, requestedImageInByte.size[1])]

# get newImage's width and height
#    width, height = requestedImageInByte.size
#    rate = round(width/height, 2)
#    newWidth = 100
#    newHeight = int(100 * rate)

# create newImage
#    newImage = Image.new("RGB", (newWidth, newHeight), randomPixel)

# upload
#    stream = io.BytesIO()
#    newImage.save(stream, format="png")
#    stream.seek(0)
#    key = "testFileNew.png"
#    s3.put_object(Bucket=bucket, Key=key, Body =stream,ContentType='image/png',ACL='public-read')

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


def addDataToPayloadFormat(data):
    payload = initializePayload()
    for newKey, newValue in list(data.items()):
        addNewKeyValueToPayloadBody(key=newKey, value=newValue, payload=payload)
    return payload


def initializePayload():
    return {
        "Records": [
            {
                "s3": {
                    "object": {
                        "body": {
                        },
                    },
                },
                "awsRegion": "ap-northeast-2"
            }
        ]
    }


def addNewKeyValueToPayloadBody(key, value, payload):
    payload['Records'][0]['s3']['object']['body'][key] = value
    return payload

#Used
def getTargetValueFromEvent(target, event):
    return event['Records'][0]['s3']['object']['body'][target]


def createDateRangeList(yearRange):
    dateList = []
    for i in range(yearRange):
        year = 2018 - i
        early = ((year, 1, 1), (year, 6, 30))
        dateList.append(early)
        late = ((year, 7, 1), (year, 12, 31))
        dateList.append(late)
    return dateList

#Used
def create_key_for_pixeled_image(url):
    print("__getStringAfterTheLastSlash function start__")
    print(url.rsplit('/', 6))
    new_key = (url.rsplit('/', 6)[-6] + "/" +
               url.rsplit('/', 6)[-5] + "/" +
               url.rsplit('/', 6)[-4] + "/" +
               "pixeled" + "/" +
               url.rsplit('/', 6)[-2] + "/" +
               url.rsplit('/', 6)[-1])
    print(new_key)
    return new_key

#requestedImage = getResponse("https://s3.ap-northeast-2.amazonaws.com/searched-words/icrawler/images/happy/original/2018_1_1-2018_6_30/000002.jpg").read()
#getRandomPixeledImageFromOriginalImageURL(requestedImage)

s3_resource = boto3.resource('s3')
my_bucket = s3_resource.Bucket('searched-words')
for object_summary in my_bucket.objects.filter(Prefix="icrawler/images/happy/pixeled/"):
        print (object_summary.key)
