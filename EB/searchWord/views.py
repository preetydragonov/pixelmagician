from __future__ import unicode_literals
from django.shortcuts import render
from django.http import HttpResponse
from PIL import Image
import urllib.request
import urllib.parse
import io
import random
import json
import time
import boto3
from .constants import (APPNAME,
                        HTML,
                        KEY,
                        URL)
from .apiRequests import (putImagesToS3,
                          getImagesFromS3)
from .logics import (getRandomPixeledImageFromImageURL)

def home(request):
    template_name = (APPNAME().SEARCHWORD
                     + "/"
                     + HTML().HOME)
    context = {}
    return render(request, 
                  template_name,
                  context)

def loading(request, queryWord):    
    parsedQueryWord = urllib.parse.unquote(queryWord)
    putImagesToS3(parsedQueryWord)

    template_name = (APPNAME().SEARCHWORD
                     + "/"
                     + HTML().LOADING)
    context = {KEY().QUERY_WORD : parsedQueryWord}

    return render(request,
                  template_name, 
                  context)

def pixelBoard(request, queryWord):
    parsedQueryWord = urllib.parse.unquote(queryWord)
    #imageUrls = getImagesFromS3(parsedQueryWord)
    imageUrls = []
    MINIMUM_IMAGES = 20
    s3_resource = boto3.resource('s3')
    my_bucket = s3_resource.Bucket('searched-words')

    while(True):
        if(len(list(my_bucket.objects.filter(Prefix="icrawler/images/" + parsedQueryWord + "/pixeled/"))) > MINIMUM_IMAGES):
            break
        else:
            time.sleep(1)



    for object_summary in my_bucket.objects.filter(Prefix="icrawler/images/" + parsedQueryWord + "/pixeled/"):
        url = "https://s3.ap-northeast-2.amazonaws.com/searched-words/" + object_summary.key
        imageUrls.append(url)

    #for n in range(600):
    #    url = "https://s3.ap-northeast-2.amazonaws.com/searched-words/testFiles/test_" + str(n) + ".png"
    #    imageUrls.append(url)

    #changedImages = []
    #for url in urls:
    #    changedImages.append(getRandomPixeledImageFromImageURL(url))    
    #aa = "<img src=\"http://lghttp.45413.nexcesscdn.net/801B14E/images/media/catalog/product/cache/1/image/9df78eab33525d08d6e5fb8d27136e95/c/h/cheese-yellow-american.jpg\"/>" 
    
    template_name = (APPNAME().SEARCHWORD
                     + "/"
                     + HTML().AFTER_SEARCHING_WORD)    
    context = {KEY().IMAGES : imageUrls}
    return render (request, 
                   template_name,
                   context)
