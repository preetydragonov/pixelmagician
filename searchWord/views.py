from __future__ import unicode_literals
from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse

def home(request):
    return render(request, 'searchWord/home_3.html', {})

def pixelBoard(request):
    return render (request, 'searchWord/pixelBoard.html',{})
