from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import RoomSerializer, CreateRoomSerializer
from .models import Room
from django.db.models.query import QuerySet
from django.http import HttpRequest
from rest_framework.views import APIView

# Create your views here.


class RoomView(generics.ListAPIView):
    queryset: QuerySet = Room.objects.all()
    serializer_class = RoomSerializer 

class CreateRoomView(APIView):
    serializer_class = CreateRoomSerializer

    def post(self, request: HttpRequest, format=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            guest_can_pause: bool = serializer.data.get('guest_can_pause')
            votes_to_skip: int = serializer.data.get('votes_to_skip')
            host: str = self.request.session.session_key
            queryset: QuerySet = Room.objects.filter(host=host)
            if queryset.exists():
                room: Room = queryset[0]
                room.guest_can_pause = guest_can_pause
                room.votes_to_skip = votes_to_skip
                room.save(update_fields=['guest_can_pause', 'votes_to_skip'])

                return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)
            else:
                room = Room(host=host, guest_can_pause=guest_can_pause, votes_to_skip=votes_to_skip)
                room.save()
                return Response(RoomSerializer(room).data, status=status.HTTP_201_CREATED)

        return Response({'Bad Request': 'Invalid data...'}, status=status.HTTP_400_BAD_REQUEST)





