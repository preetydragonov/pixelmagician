import urllib.request
from PIL import Image
import io
from django.http import HttpResponse

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
