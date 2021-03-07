from django.shortcuts import render, redirect
from django.http import HttpRequest
from .credentials import REDIRECT_URI, CLIENT_ID, CLIENT_SECRET
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from requests import Request, post
from typing import Dict
from .util import *
from api.models import Room

# Create your views here.
class AuthURL(APIView):
    def get(self, request: HttpRequest, format=None) -> Response:
        scopes: str = 'user-read-playback-state user-modify-playback-state user-read-currently-playing'

        url: str = Request('GET', 'https://accounts.spotify.com/authorize', params={
            'scope': scopes,
            'response_type': 'code',
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID
        }).prepare().url

        return Response({'url': url}, status=status.HTTP_200_OK)

def spotify_callback(request: HttpRequest, format=None):
    code: str = request.GET.get('code')
    error: str = request.GET.get('error')

    response: Dict = post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }).json()

    access_token: str = response.get('access_token')
    token_type: str = response.get('token_type')
    refresh_token: str = response.get('refresh_token')
    expires_in: float = response.get('expires_in')
    error: str = response.get('error')

    if not request.session.exists(request.session.session_key):
        request.session.create()

    update_or_create_user_tokens(
        request.session.session_key, access_token, token_type, expires_in, refresh_token)

    return redirect('frontend:')

class IsAuthenticated(APIView):
    def get(self, request: HttpRequest, format=None) -> Response:
        is_authenticated: bool = is_spotify_authenticated(
            self.request.session.session_key)
        return Response({'status': is_authenticated}, status=status.HTTP_200_OK)

class CurrentSong(APIView):
    def get(self, request: HttpRequest, format=None) -> Response:
        room_code: str = self.request.session.get('room_code')
        # check if requester is host or not
        room: QuerySet = Room.objects.filter(code=room_code)
        if room.exists():
            room: Room = room[0] 
        else:
            return Response({}, status=status.HTTP_404_NOT_FOUND)   
        host: str = room.host
        endpoint: str = "player/currently-playing"
        response: Dict = execute_spotify_api_request(host, endpoint)
        print(response)

        return Response(response, status=status.HTTP_200_OK)



