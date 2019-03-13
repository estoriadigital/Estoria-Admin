from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('transcriptions', views.transcriptions, name='transcriptions'),
    path('readerxml', views.readerxml, name='readerxml'),
    path('baking', views.baking, name='baking'),
    path('critical', views.critical, name='critical'),
]
