from django.db.models.query import QuerySet
from django.utils import timezone
from .models import SpotifyToken
from datetime import timedelta, datetime

def get_user_tokens(session_id: str) -> Optional[SpotifyToken]:
    user_tokens: QuerySet = SpotifyToken.objects.filter(user=session_id)
    print(user_tokens)
    if user_tokens.exists():
        return user_tokens[0]
    else:
        return None

def update_or_create_user_tokens(session_id: str, access_token: str, token_type: str, expires_in: float, refresh_token: str):
    tokens: SpotifyToken = get_user_tokens(session_id)
    expires_in: datetime = timezone.now() + timedelta(seconds=expires_in)

    if tokens:
        tokens.access_token = access_token
        tokens.refresh_token = refresh_token
        tokens.expires_in = expires_in
        tokens.token_type = token_type
        tokens.save(update_fields=['access_token',
                                   'refresh_token', 'expires_in', 'token_type'])

    else:
        tokens = SpotifyToken(user=session_id, access_token=access_token,
                              refresh_token=refresh_token, token_type=token_type, expires_in=expires_in)
        tokens.save()
