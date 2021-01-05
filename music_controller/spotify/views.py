from django.shortcuts import render, redirect
from django.http import HttpRequest, JsonResponse
from .credentials import CLIENT_ID, CLIENT_SECRET,REDIRECT_URI
from rest_framework.views import APIView
import requests
from requests import Request, post
from rest_framework import status
from rest_framework.response import Response
from requests.models import PreparedRequest
from api.models import Room
from .util import *
from typing import Dict, Union
import json
# Create your views here.

# VIEW THAT WILL authenticate our app or request access
class AuthURL(APIView):
    def get(self, request: Request, format=None) -> JsonResponse:
        # scope is what info we wanna access(spotify docs)
        scopes = 'user-read-playback-state user-modify-playback-state user-read-currently-playing'

        url: PreparedRequest.url = Request('GET', 'https://accounts.spotify.com/authorize', params={
            'scope': scopes,
            'response_type': 'code',
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
        }).prepare().url
        print(url)
        # we're nt sending the request cause it will have to arrive to the frontend first
        return Response({'url': url}, status=status.HTTP_200_OK)

# we need an endpoint(callback) can can take the (code, state) from the authorization access uopn logging-in
# and returns the access and refresh tokens
def spotify_callback(request: HttpRequest, format=None):
    code: str = request.GET.get('code')
    error: str = request.GET.get('error')

    response: requests.Response = post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }).json()

    access_token = response.get('access_token')
    token_type = response.get('token_type')
    refresh_token = response.get('refresh_token')
    expires_in = response.get('expires_in')
    error = response.get('error')

    if not request.session.exists(request.session.session_key):
        request.session.create()

    # let's update the fields
    update_or_create_user_tokens(
        request.session.session_key, access_token, token_type, expires_in, refresh_token
    )

    return redirect('frontend:')

# a view to check if user is authentcated
class IsAuthenticated(APIView):
    def get(self, request: HttpRequest, format=None) -> Union[JsonResponse, Response]:
        is_authenticated: bool = is_spotify_authenticated(
            self.request.session.session_key)
        
        return Response(data={'is_auth': is_authenticated}, status=status.HTTP_200_OK)

        
        # return Response({'Invalid request': 'not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

    
# returns info about the current song
class CurrentSong(APIView):
    def get(self, request: HttpRequest, format=None):
        room_code = self.request.session.get('room_code')
        room: Room = Room.objects.filter(code=room_code)
        if room.exists():
            room = room[0]
        else:
            return Response({}, status=status.HTTP_200_OK)
        host: str = room.host
        # specify the endpoint to access songs from spotify api
        endpoint = "player/currently-playing"
        response: Dict = execute_spotify_api_request(host, endpoint)
        print(response)

        return Response(response, status=status.HTTP_200_OK)




    


