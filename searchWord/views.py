from __future__ import unicode_literals
from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse

def home(request):
    return render(request, 'searchWord/home_3.html', {})

def pixelBoard(request):
    image_1 = "http://media-cache-ec0.pinimg.com/736x/d6/1f/6f/d61f6ff7dc676504170e6233fc6373e6.jpg"
    return render (request, 'searchWord/index.html',{'image_1': image_1})
