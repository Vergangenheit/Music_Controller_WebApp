from django.db import models
from django.db.models import CharField, DateTimeField
# Create your models here.

# we need to make a model to store tokens
class SpotifyToken(models.Model):
    user: CharField = models.CharField(max_length=50, unique=True)
    created_at: DateTimeField = models.DateTimeField(auto_now_add=True)
    refresh_token: CharField = models.CharField(max_length=150)
    access_token: CharField = models.CharField(max_length=150)
    expires_in: DateTimeField = models.DateTimeField()
    token_type: CharField = models.CharField(max_length=50)