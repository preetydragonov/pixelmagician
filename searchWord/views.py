from __future__ import unicode_literals
from django.shortcuts import render
from django.http import HttpResponse
from PIL import Image
import urllib.request
import urllib.parse
import io
import random
import json

def home(request):
    return render(request, 'searchWord/home.html', {})

def loading(request, user_id):
    decoded_user_id = urllib.parse.unquote(user_id)
    data = formatData(data=decoded_user_id, request="POST")
    request_postImage = urllib.request.Request('https://gemq3v63g6.execute-api.ap-northeast-2.amazonaws.com/prod/image', data)
    response_postImage = urllib.request.urlopen(request_postImage)
    return render(request, 'searchWord/loading.html', {'user_id':decoded_user_id})

def formatData(data, request):
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

    if(request == 'POST'):
        jsonFormattedData = json.dumps(formattedData)
        encodedFormattedData = jsonFormattedData.encode('utf-8')
        return encodedFormattedData
    elif(request == 'GET'):
        params = urllib.parse.urlencode(formattedData)
        return params
    else:
        return null;

def pixelBoard(request, user_id):
    decoded_user_id = urllib.parse.unquote(user_id)
    url = "https://gemq3v63g6.execute-api.ap-northeast-2.amazonaws.com/prod/image"
    request_getImage = urllib.request.Request(url+"?key=" + decoded_user_id + ".json")
    response_getImage = urllib.request.urlopen(request_getImage).read()
    
    imageUrls = json.loads(response_getImage)
    #changedImages = []
    #for url in urls:
    #    changedImages.append(getRandomPixeledImageFromImageURL(url))    
    aa = "<img src=\"http://lghttp.45413.nexcesscdn.net/801B14E/images/media/catalog/product/cache/1/image/9df78eab33525d08d6e5fb8d27136e95/c/h/cheese-yellow-american.jpg\"/>" 
    return render (request, 'searchWord/index.html', {'images': imageUrls[0:10]})


def getRandomPixeledImageFromImageURL(url):
    requestedImage = urllib.request.urlopen(urllib.request.Request(url)).read()
    image = Image.open(io.BytesIO(requestedImage))
    pixel = image.load()
    randomPixel = pixel[random.randint(0, image.size[0]), random.randint(0, image.size[1])]
   
    # Change Image Into One Pixel
    #for i in range(image.size[0]):
    #    for j in range(image.size[1]):
    #        pixel[i,j] = randomPixel
    
    image = Image.new('RGB', (image.size[0], image.size[1]), 0)

    # Saving the image to the Django response object:
    response = HttpResponse(content_type='image/png')
    image.save(response, 'PNG')
    
    return image
    



