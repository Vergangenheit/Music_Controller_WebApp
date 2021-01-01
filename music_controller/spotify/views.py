from django.shortcuts import render, redirect
from django.http import HttpRequest
from .credentials import CLIENT_ID, CLIENT_SECRET,REDIRECT_URI
from rest_framework.views import APIView
import requests
from requests import Request, post
from rest_framework import status
from rest_framework.response import Response
from requests.models import PreparedRequest
from .util import update_or_create_user_tokens, get_user_tokens, is_spotify_authenticated
# Create your views here.

# VIEW THAT WILL authenticate our app or request access
class AuthURL(APIView):
    def get(self, request: Request, format=None) -> Response:
        # scope is what info we wanna access(spotify docs)
        scopes = 'user-read-playback-state user-modify-playback-state user-read-currently-playing'

        url: PreparedRequest.url = Request('GET', 'https://accounts.spotify.com/authorize', params={
            'scope': scopes,
            'response_type': 'code',
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
        }).prepare().url
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
    def get(self, request: HttpRequest, format=None):
        # we're callin the util function
        is_authenticated: bool = is_spotify_authenticated(self.request.session.session_key)
        return Response({'status': is_authenticated}, status=status.HTTP_200_OK)

    






    


