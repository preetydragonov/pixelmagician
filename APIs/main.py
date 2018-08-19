# -*-encoding: utf-8 -*-
import json
import urllib.parse
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import urllib.request
import boto3
from botocore.errorfactory import ClientError
import random
from random import randint
import io
from PIL import Image
import ssl
from icrawler.builtin import GoogleImageCrawler
import os
from os import path
from k_means import (get_points,
                      kmeans)
from base64 import b64encode

s3 = boto3.client('s3')
bucket = 'searched-words'
Lambda = boto3.client('lambda')

def post_searched_word_to_slack(event, context):
    # The base-64 encoded, encrypted key (CiphertextBlob) stored in the kmsEncryptedHookUrl environment variable
    #ENCRYPTED_HOOK_URL = os.environ['kmsEncryptedHookUrl']
    SLACK_CHANNEL = 'get-searched-word'
    HOOK_URL = "https://hooks.slack.com/services/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"
    word = event['Records'][0]['lambda-invoke']['word']
    slack_message = {
        'channel': SLACK_CHANNEL,
        'text': word
    }
    req = Request(HOOK_URL, json.dumps(slack_message).encode('utf-8'))
    try:
        response = urlopen(req)
        response.read()
    except HTTPError as e:
        print(e)
        raise e
    except URLError as e:
        print(e)
        raise e

def put_pixels_to_s3(event, context):
    try:
        image_url = getTargetValueFromEvent(target="image_url", event=event)
    except Exception as exception:
        print("Cannot get value of key 'image_url' from event.")
        raise exception
    try:
        original_key = getTargetValueFromEvent(target="original_key", event=event)
    except Exception as exception:
        print("Cannot get value of key 'key' from event.")
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
        pixeled_image_stream = getPixeledImageFromOriginalImageURL(requested_image, process_type="DOMINANT")
    except Exception as exception:
        print("Cannot get random pixeled image.")
        raise exception
    try:
        pixeled_key = create_key_for_pixeled_image(original_key)
        s3.put_object(Bucket=bucket,
                      Key=pixeled_key,
                      Body=pixeled_image_stream,
                      ContentType='image/jpeg',
                      ACL='public-read')
    except Exception as exception:
        print("Cannot put object To S3.")
        raise exception


def put_images_to_s3_by_using_icrawler(event, context):
    try:
        print(event)
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

    directory = create_directory(query_word, date_range_in_tuple)

    try:
        s3.head_object(Bucket=bucket, Key='icrawler/' + directory + '/000001.jpg')
        print(query_word + " exists! Sombody queried this word before. So, I will stop here and give out priviously saved images.")
        return
    except ClientError:
        print(query_word + " does not exist! So, I will save new pixel images of it.")
        pass

    google_crawler = GoogleImageCrawler(downloader_threads=3, storage={'root_dir': '/tmp/' + directory})
    google_crawler.crawl(query_word, filters=dict(date=date_range_in_tuple), max_num=max_iteration)
    print("crawl ended")

    for i in list(range(1, max_iteration+1)):
        file_path = '/tmp/' + directory + '/00000{}.jpg'.format(i)
        if(path.exists(file_path)):
            original_key = 'icrawler/' + directory + '/' + '00000{}.jpg'.format(i)
            try:
                s3.upload_file(file_path, Bucket=bucket, Key=original_key, ExtraArgs={'ACL':'public-read'})
                print("uploaded file to S3")
            except Exception as exception:
                print('Error getting object {} from bucket {}.'.format(original_key, bucket))
                raise exception

            image_url = "https://s3.ap-northeast-2.amazonaws.com/searched-words/icrawler/" + get_korean_converted_to_unicode(query_word, date_range_in_tuple) + '/' + '00000{}.jpg'.format(i)
            
            payload = addDataToPayloadFormat(data={"image_url": image_url, "original_key": original_key})
            
            try:
                Lambda.invoke(FunctionName="APIs-dev-put_pixels_to_s3",
                              InvocationType='Event',
                              Payload=json.dumps(payload))
                print("triggered pixel uploading function")
            except Exception as exception:
                raise exception

def create_directory(query_word, date_range_in_tuple):
    return (
        'images/' + query_word + "/" +
        'original' + '/' +
        str(date_range_in_tuple[0][0]) + '_' + str(date_range_in_tuple[0][1]) + '_' + str(date_range_in_tuple[0][2]) +
        "-" +
        str(date_range_in_tuple[1][0]) + '_' + str(date_range_in_tuple[1][1]) + '_' + str(date_range_in_tuple[1][2])
    )

def get_korean_converted_to_unicode(query_word, date_range_in_tuple):
    return (
        'images/' + urllib.parse.quote_plus(query_word) + "/" +
        'original' + '/' +
        str(date_range_in_tuple[0][0]) + '_' + str(date_range_in_tuple[0][1]) + '_' + str(date_range_in_tuple[0][2]) +
        "-" +
        str(date_range_in_tuple[1][0]) + '_' + str(date_range_in_tuple[1][1]) + '_' + str(date_range_in_tuple[1][2])
    )


def icrawler_trigger(event, context):
    try:
        query_word = getTargetValueFromEvent(target="query_word", event=event)
    except Exception as exception:
        print("Cannot get value of key 'query_word' from event.")
        raise exception
    try:
        date_range = getTargetValueFromEvent(target="date_range", event=event)
    except Exception as exception:
        print("Cannot get value of key 'date_range' from event.")
        raise exception

    payload = addDataToPayloadFormat(data={"query_word": query_word,
                                           "date_range": date_range,
                                           "max_iteration": 3})

    Lambda.invoke(FunctionName="APIs-dev-put_images_to_s3_by_using_icrawler",
                  InvocationType='Event',
                  Payload=json.dumps(payload))


def put_images_to_S3(event, context):
    print(event)
    queryWord = event['Records'][0]['s3']['object']['body']
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

def getPixeledImageFromOriginalImageURL(requested_image, process_type):
    opened_image = openImage(requested_image)
    if process_type == "RANDOM":
        print("extract pixel randomly.")
        pixel = get_random_pixel(opened_image)
    elif process_type == "MAX_FREQUENT":
        print("extract the most frequent pixel.")
        pixel = get_max_frequent_pixel(opened_image)
    elif process_type == "DOMINANT" :
        print("extract the most dominant pixel.")
        pixel = get_dominant_pixel(opened_image)
    else:
        print("pixel type is not suggested. just using random way.")
        pixel = get_random_pixel(opened_image)

    if not isinstance(pixel, tuple):
        print("pixel not in tuple form")
        pixel = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    if len(pixel) < 3:
        print("pixel length less than 3")
        pixel = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    stream = io.BytesIO()
    pixeled_image = createPixeledImageInSmallerSize(opened_image, pixel)
    pixeled_image.save(stream, format="jpeg")
    stream.seek(0)
    return stream

def get_dominant_pixel(imageInByte, n=5):
    imageInByte.thumbnail((200, 200))
    points = get_points(imageInByte)
    clusters = kmeans(points, n, 1)
    dominant_pixels = [map(int, c.center.coords) for c in clusters]

    white = 255*3
    non_white_vivid_pixels = []
    white_pixels = []

    for pixel in dominant_pixels:
        dominant_pixel = list(pixel)
        if sum(dominant_pixel) < white - 50:
            non_white_vivid_pixels.append(dominant_pixel)
        else:
            white_pixels.append(dominant_pixel)

    if len(non_white_vivid_pixels) != 0 :
        randomly_picked_dominant_and_vivid_pixel = non_white_vivid_pixels[randint(0, len(non_white_vivid_pixels) -1)]
        return tuple(randomly_picked_dominant_and_vivid_pixel)
    else:
        randomly_picked_white_pixel = white_pixels[randint(0, len(white_pixels) -1)]
        return tuple(randomly_picked_white_pixel)

def get_random_pixel(imageInByte):
    pixels = imageInByte.load()
    width, height = imageInByte.size
    randomPixel = pixels[random.randint(0, width), random.randint(0, height)]
    return randomPixel

def get_max_frequent_pixel(imageInByte):
    width, height = imageInByte.size
    colors = imageInByte.getcolors(width * height) #put a higher value if there are many colors in your image
    max_occurence, most_present = 0, 0
    try:
        for c in colors:
            if c[0] > max_occurence:
                (max_occurence, most_present) = c
        return most_present
    except TypeError:
        raise Exception("Too many colors in the image")

def openImage(image):
    imageInBytes = io.BytesIO(image)
    return Image.open(imageInBytes)

def createPixeledImageInSmallerSize(imageInByte, randomPixel):
    width, height = imageInByte.size
    rate = round(width / height, 2)
    new_height = 300
    new_width = int(new_height * rate)
    return Image.new("RGB", (new_width, new_height), randomPixel)


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


def getTargetValueFromEvent(target, event):
    return event['Records'][0]['s3']['object']['body'][target]


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

#s3_resource = boto3.resource('s3')
#my_bucket = s3_resource.Bucket('searched-words')
#for object_summary in my_bucket.objects.filter(Prefix="icrawler/images/happy/pixeled/"):
#        print (object_summary.key)
