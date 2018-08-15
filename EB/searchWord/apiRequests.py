import json
from .constants import (APPNAME,
                        HTML,
                        KEY,
                        URL)
from urllib.request import Request, urlopen
from urllib.parse import urlencode
import asyncio


def sendQueryWordToSlack(queryWord):
    formattedQueryWord = formatDataForSlackRequest(queryWord, requestType="POST")
    request = Request(URL().POST_SEARCHED_WORD_TO_SLACK, formattedQueryWord)
    urlopen(request)

def internet_resource_getter(post_data):
    request = Request(URL().ICRAWLER_TRIGGER, post_data)
    urlopen(request)

def putImagesToS3(data):
    postData = []
    for date_range in createDateRangeList(7):
        postDatum = formatDataForS3Request(data, date_range, requestType="POST")
        postData.append(postDatum)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    for postDatum in postData:
        loop.run_in_executor(None, internet_resource_getter, postDatum)

    # requestsForPutImages = []
    #
    # for date_range in createDateRangeList(7):
    #     request = Request(URL().ICRAWLER_TRIGGER,
    #                               formatDataForS3Request(data,
    #                                                      date_range,
    #                                                      requestType="POST"))
    #     requestsForPutImages.append(request)
    #
    # # requestForPutImages = Request(URL().ICRAWLER_TRIGGER,
    # #                               formatDataForS3Request(data,
    # #                                                      date_ranges[0],
    # #                                                      requestType="POST"))
    #
    #
    #
    # urlopen(requestForPutImages)

def getImagesFromS3(searchedWord):
    requestForGetImages = Request(URL().GET_IMAGES_FROM_S3
                                              + "?key=" 
                                              + searchedWord 
                                              + ".json")
    response = urlopen(requestForGetImages).read()
    imageUrls = json.loads(response)
    
    return imageUrls


def createDateRangeList(yearRange):
    dateList = []
    for i in range(yearRange):
        year = 2018 - i
        for month in range(1, 13):
        early = ((year, month, 1), (year, month, 15))
        dateList.append(early)
        late = ((year, month, 1), (year, month, 30))
        dateList.append(late)
    return dateList

def formatDataForS3Request(data, date_range, requestType):
    formattedData = {
        "Records": [{
            "s3": {
                "object": {
                    "body": {
                        'query_word': data,
                        'date_range': date_range
                    }
                },
                "s3SchemaVersion": "1.0"
            },
            "awsRegion": "ap-northeast-2"
        }]
    }

    if(requestType == 'POST'):
        return json.dumps(formattedData).encode('utf-8')

    elif(requestType == 'GET'):
        params = urlencode(formattedData)
        return params
    
    else:
        return

def formatDataForSlackRequest(queryWord, requestType):
    formattedData = {
        "Records": [{
            "lambda-invoke": {
                'word': queryWord,
            },
        }]
    }
    if(requestType == 'POST'):
        return json.dumps(formattedData).encode('utf-8')

    elif(requestType == 'GET'):
        params = urlencode(formattedData)
        return params

    else:
        return

