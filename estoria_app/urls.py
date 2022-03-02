from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('transcriptions', views.transcriptions, name='transcriptions'),
    path('readerxml', views.readerxml, name='readerxml'),
    re_path(r'apparatus/?$', views.apparatus, name='apparatus'),
    re_path(r'apparatus/chapter/(?P<chapter>\d+)/?$', views.chapter, name='chapter'),
    re_path(r'apparatus/(?P<context>D\d+S.+)/?$', views.sentence, name='sentence'),
    path('critical', views.critical, name='critical'),
]
