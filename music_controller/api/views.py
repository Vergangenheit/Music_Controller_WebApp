from django.shortcuts import render
from django.db.models.query import QuerySet
from django.db.models.manager import BaseManager
from requests import Request
from django.http import HttpResponse, JsonResponse
from rest_framework import generics, status
from .models import Room
from .serializers import RoomSerializer, CreateRoomSerializer, UpdateRoomSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.serializers import ReturnDict
from rest_framework.request import HttpRequest
from typing import Dict


# Create your views here.
class RoomView(generics.ListAPIView):
    """it's a view that returns all different rooms"""
    queryset: QuerySet = Room.objects.all()
    serializer_class = RoomSerializer

class GetRoom(APIView):
    serializer_class = RoomSerializer
    lookup_url_kwarg: str = 'code'

    def get(self, request: HttpRequest, format=None):
        code: str = request.GET.get(self.lookup_url_kwarg)
        if code != None:
            room: QuerySet = Room.objects.filter(code=code)
            if len(room) > 0:
                data: ReturnDict = RoomSerializer(room[0]).data
                data['is_host']: str = self.request.session.session_key == room[0].host
                return Response(data, status=status.HTTP_200_OK)
            return Response({'Room Not Found': 'Invalid Room Code.'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'Bad Request': 'Code parameter note found in request'}, status=status.HTTP_400_BAD_REQUEST)

class JoinRoom(APIView):
    lookup_url_kwarg = 'code'

    def post(self, request: HttpRequest, format=None):
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
    serializer_class: CreateRoomSerializer = CreateRoomSerializer

    def post(self, request: HttpRequest, format=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()

        serializer: CreateRoomSerializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            guest_can_pause: bool = serializer.data.get('guest_can_pause')
            votes_to_skip: int = serializer.data.get('votes_to_skip')
            host = self.request.session.session_key
            queryset: QuerySet = Room.objects.filter(host=host)
            if queryset.exists():
                room: Room = queryset[0]
                room.guest_can_pause: bool = guest_can_pause
                room.votes_to_skip: int = votes_to_skip
                room.save(update_fields=['guest_can_pause', 'votes_to_skip'])
                self.request.session['room_code'] = room.code
                return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)
            else:
                room: Room = Room(host=host, guest_can_pause=guest_can_pause,
                            votes_to_skip=votes_to_skip)
                room.save()
                self.request.session['room_code'] = room.code
                return Response(RoomSerializer(room).data, status=status.HTTP_201_CREATED)

        return Response({'Bad Request': 'Invalid data...'}, status=status.HTTP_400_BAD_REQUEST)

class UserInRoom(APIView):
    def get(self, request: HttpRequest,format=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()

        data: Dict = {
            'code': self.request.session.get('room_code')
        }

        return JsonResponse(data, status=status.HTTP_200_OK)

class LeaveRoom(APIView):
    def post(self, request: HttpRequest, format=None):
        if 'room_code' in self.request.session:
            self.request.session.pop('room_code')
            host_id: str = self.request.session.session_key
            # check if the user who's leaving is the room host, if so kick everyone out of the room
            room_results: QuerySet = Room.objects.filter(host=host_id)
            if len(room_results) > 0:
                room: Room = room_results[0]
                room.delete()

        return Response({'message': 'Success'}, status=status.HTTP_200_OK)

class UpdateRoom(APIView):
    serializer_class = UpdateRoomSerializer
    # patch it's an update action
    def patch(self, request: HttpRequest, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            guest_can_pause = serializer.data.get('guest_can_pause')
            votes_to_skip = serializer.data.get('votes_to_skip')
            code = serializer.data.get('code')

            # find a room that has the same code
            queryset: QuerySet = Room.objects.filter(code=code)
            if not queryset.exists():
                return Response({'msg': 'Room not found.'}, status=status.HTTP_404_NOT_FOUND)
            
            room: Room = queryset[0]
            user_id: str = self.request.session.session_key
            if room.host != user_id:
                return Response({'msg': 'You are not the host of this room'}, status=status.HTTP_403_FORBIDDEN)
            # we can update the room
            room.guest_can_pause = guest_can_pause
            room.votes_to_skip = votes_to_skip
            room.save(update_fields=['guest_can_pause', 'votes_to_skip'])
            return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)

        return Response({'Bad Request': "Invalid data..."}, status=status.HTTP_400_BAD_REQUEST)    