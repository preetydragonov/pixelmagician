from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^board/(?P<queryWord>\w+)', views.pixelBoard, name='pixelBoard'),
    url(r'^loading/(?P<queryWord>\w+)/$', views.loading, name='loading'),
        ]
