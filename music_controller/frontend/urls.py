from django.urls import path
from .views import index
from typing import List

app_name = 'frontend'

urlpatterns: List = [
    path('', index, name=''),
    path('join', index),
    path('create', index),
    path('room/<str:roomCode>', index)
]