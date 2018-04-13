from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^board/(?P<user_id>\w+)', views.pixelBoard, name='pixelBoard'),
    url(r'^loading/(?P<user_id>\w+)/$', views.loading, name='loading'),
        ]
