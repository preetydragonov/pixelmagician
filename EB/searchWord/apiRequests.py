import json
import urllib.request
from .constants import (APPNAME,
                        HTML,
                        KEY,
                        URL)

def putImagesToS3(data):
    formattedDataForPuttingOnS3 = formatDataForS3Request(data, requestType="POST")
    requestForPutImages = urllib.request.Request(URL().PUT_IMAGES_TO_S3, formattedDataForPuttingOnS3)
    response = urllib.request.urlopen(requestForPutImages)

def getImagesFromS3(searchedWord):
    requestForGetImages = urllib.request.Request(URL().GET_IMAGES_FROM_S3
                                              + "?key=" 
                                              + searchedWord 
                                              + ".json")
    response = urllib.request.urlopen(requestForGetImages).read()
    imageUrls = json.loads(response)
    
    return imageUrls

def formatDataForS3Request(data, requestType):
    formattedData = {
        "Records": [{
            "s3": {
                "object": {
                    "body": {
                        'query_word': data
                    }
                },
                "s3SchemaVersion": "1.0"
            },
            "awsRegion": "ap-northeast-2"
        }]
    }

    if(requestType == 'POST'):
        jsonFormattedData = json.dumps(formattedData)
        encodedFormattedData = jsonFormattedData.encode('utf-8')
        return encodedFormattedData

    elif(requestType == 'GET'):
        params = urllib.parse.urlencode(formattedData)
        return params
    
    else:
        return null;

