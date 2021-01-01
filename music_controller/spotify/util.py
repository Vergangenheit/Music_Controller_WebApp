from .models import SpotifyToken
from django.db.models.manager import BaseManager
from django.db.models.query import QuerySet
from django.utils import timezone
from datetime import timedelta, datetime
import requests
from requests import post
from .credentials import CLIENT_ID, CLIENT_SECRET

BASE_URL = "https://api.spotify.com/v1/me/"

def get_user_tokens(session_id: str)-> SpotifyToken:
    user_tokens: QuerySet = SpotifyToken.objects.filter(user=session_id)
    if user_tokens.exists():
        return user_tokens[0]
    else:
        return None

# saves our tokens in a model
def update_or_create_user_tokens(sessions_id: str, access_token: str, token_type: str, expires_in: datetime, refresh_token: str):
    # see if user has any preexisting tokens
    tokens: SpotifyToken = get_user_tokens(session_id)
    expires_in: datetime = timezone.now() + timedelta(seconds=expires_in) # expires_in returned by spotify api is 1h by default

    if tokens:
        # update db
        tokens.access_token = access_token
        tokens.refresh_token = refresh_token
        tokens.expires_in = expires_in
        tokens.token_type = token_type
        tokens.save(update_fields=['access_token',
                                   'refresh_token', 'expires_in', 'token_type'])

    else:
        # create new token
        tokens: SpotifyToken = SpotifyToken(user=session_id, access_token=access_token,
                              refresh_token=refresh_token, token_type=token_type, expires_in=expires_in)           
        tokens.save()

# check if user is authent in spotify
def is_spotify_authenticated(session_id: str) -> bool:
    tokens: SpotifyToken = get_user_tokens(session_id)
    if tokens:
        expiry: datetime = tokens.expires_in
        if expiry <= timezone.now():
            # refresh the tokens
            refresh_spotify_token(tokens)

        return True

    return False

def refresh_spotify_token(session_id: str):
    refresh_token: str = get_user_tokens(session_id).refresh_token

    response: requests.Response = post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }).json()

    access_token: str = response.get('access_token')
    token_type: str = response.get('token_type')
    expires_in: datetime = response.get('expires_in')
    refresh_token: str = response.get('refresh_token')

    update_or_create_user_tokens(
        session_id, access_token, token_type, expires_in, refresh_token)


