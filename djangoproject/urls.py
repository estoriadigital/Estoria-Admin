"""
djangoproject URL Configuration
"""
from django.urls import include, path, re_path
from .shared import poll_state
from . import views
from estoria_app import views as admin_views

urlpatterns = [
    path('', views.index, name='base'),
    path('xmlconversion/', include('xmlconversion_app.urls')),
    path('estoria-admin/', include('estoria_app.urls')),
    path('poll_state', poll_state, name='poll_state'),
    re_path(r'apparatus/(?P<project>\w+-digital)/chapter/(?P<chapter>\d+)/?$',
            admin_views.chapter, name='chapter'),
]
