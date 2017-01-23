# howdy/urls.py
from django.conf.urls import url
from movies_bot import views

urlpatterns = [
               url(r'^callback$', views.callback, name='callback'),
               ]
