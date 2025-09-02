from django.contrib import admin
from django.urls import path, include
from .views import BookViewSet, get_serial_ports

urlpatterns = [
    path('devicesView', BookViewSet),
    path('postsView', get_serial_ports),
]
