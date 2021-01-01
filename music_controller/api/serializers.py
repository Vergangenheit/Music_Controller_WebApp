"""translate Room object into json"""
from rest_framework import serializers
from .models import Room
from typing import Tuple

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields: Tuple = ('id', 'code', 'host', 'guest_can_pause', 'votes_to_skip')

class CreateRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        # serializes the request 
        fields: Tuple = ('guest_can_pause', 'votes_to_skip')

class UpdateRoomSerializer(serializers.ModelSerializer):
    code = serializers.CharField(validators=[])
    class Meta: 
        model = Room
        # serializes the request 
        fields: Tuple = ('guest_can_pause', 'votes_to_skip','code')

