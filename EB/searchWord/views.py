from __future__ import unicode_literals
from django.shortcuts import render
from django.http import HttpResponse
from PIL import Image
import urllib.request
import urllib.parse
import io
import random
import json
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
    imageUrls = []

    s3_resource = boto3.resource('s3')
    my_bucket = s3_resource.Bucket('searched-words')
    for object_summary in my_bucket.objects.filter(Prefix="icrawler/images/" + parsedQueryWord + "/pixeled/"):
        url = "https://s3.ap-northeast-2.amazonaws.com/searched-words/" + object_summary.key
        imageUrls.append(url)
    
    template_name = (APPNAME().SEARCHWORD
                     + "/"
                     + HTML().AFTER_SEARCHING_WORD)    
    context = {KEY().IMAGES : imageUrls}

    return render (request, 
                   template_name,
                   context)
