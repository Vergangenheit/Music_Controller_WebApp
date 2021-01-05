from django.shortcuts import render
from rest_framework import generics
from .serializers import RoomSerializer
from .models import Room
from django.db.models.query import QuerySet

# Create your views here.


class RoomView(generics.ListAPIView):
    queryset: QuerySet = Room.objects.all()
    serializer_class = RoomSerializer 