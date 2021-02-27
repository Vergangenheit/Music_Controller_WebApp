from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import RoomSerializer, CreateRoomSerializer
from .models import Room
from django.db.models.query import QuerySet
from django.http import HttpRequest
from rest_framework.views import APIView
from rest_framework.utils.serializer_helpers import ReturnDict
from typing import Dict
from django.http import JsonResponse
# Create your views here.


class RoomView(generics.ListAPIView):
    queryset: QuerySet = Room.objects.all()
    serializer_class = RoomSerializer 

class GetRoom(APIView):
    serializer_class = RoomSerializer
    lookup_url_kwarg: str = 'code'

    def get(self, request: HttpRequest, format=None) -> Response:
        code: str = request.GET.get(self.lookup_url_kwarg)
        if code != None:
            room: QuerySet = Room.objects.filter(code=code)
            if len(room) > 0:
                data: ReturnDict = RoomSerializer(room[0]).data
                data['is_host'] = self.request.session.session_key == room[0].host
                return Response(data, status=status.HTTP_200_OK)
            return Response({'Room Not Found': 'Invalid Room Code.'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'Bad Request': 'Code paramater not found in request'}, status=status.HTTP_400_BAD_REQUEST)

class JoinRoom(APIView):
    lookup_url_kwarg: str = 'code'

    def post(self, request: HttpRequest, format=None) -> Response:
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()

        code: str = request.data.get(self.lookup_url_kwarg)
        if code != None:
            room_result: QuerySet = Room.objects.filter(code=code)
            if len(room_result) > 0:
                room: Room = room_result[0]
                self.request.session['room_code'] = code
                return Response({'message': 'Room Joined!'}, status=status.HTTP_200_OK)

            return Response({'Bad Request': 'Invalid Room Code'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'Bad Request': 'Invalid post data, did not find a code key'}, status=status.HTTP_400_BAD_REQUEST)




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
                self.request.session['room_code'] = room.code
                return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)
            else:
                room = Room(host=host, guest_can_pause=guest_can_pause, votes_to_skip=votes_to_skip)
                room.save()
                self.request.session['room_code'] = room.code
                return Response(RoomSerializer(room).data, status=status.HTTP_201_CREATED)

        return Response({'Bad Request': 'Invalid data...'}, status=status.HTTP_400_BAD_REQUEST)

class UserInRoom(APIView):

    def get(self, request: HttpRequest, format=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
            
        data: Dict = {
            'code': self.request.session.get('room_code')
            }
        
        return JsonResponse(data, status=status.HTTP_200_OK)

class LeaveRoom(APIView):
    def post(self, request:  HttpRequest, format=None) -> Response:
        if 'room-code' in self.request.session:
            self.request.session.pop('room_code')
            host_id = self.request.session.session_key
            room_results: QuerySet = Room.object.filter(host=host_id)
            if len(room_results) > 0:
                room: Room = room_results[0]
                room.delete()

        return Response({'Message':'Success'}, status=status.HTTP_200_OK)





