"""
djangoproject URL Configuration
"""
from django.urls import include, path
from .shared import poll_state
from . import views

urlpatterns = [
    path('', views.index, name='base'),
    path('xmlconversion/', include('xmlconversion_app.urls')),
    path('estoria/', include('estoria_app.urls')),
    path('poll_state', poll_state, name='poll_state'),
]
