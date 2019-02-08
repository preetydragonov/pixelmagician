import json
import urllib.request
from .constants import (APPNAME,
                        HTML,
                        KEY,
                        URL)

def triggerAPI_putImagesToS3(data):
    #데이터를 리퀘스트 포멧에 맞춰 변경, 후에 리퀘스트 요청.
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
                    "key": data,
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
        return null

