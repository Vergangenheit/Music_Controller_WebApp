from django.db import models
import string
import random
from django.db.models import CharField, BooleanField, IntegerField, DateTimeField

def generate_unique_code() -> str:
    length: int = 6
    while True:
        code: str = ''.join(random.choices(string.ascii_uppercase,k=length))
        if Room.objects.filter(code=code).count() == 0:
            break

    return code


# Create your models here.
class Room(models.Model):
    code: CharField = models.CharField(max_length=8, default=generate_unique_code, unique=True)
    host: CharField = models.CharField(max_length=50, unique=True)
    guest_can_pause = models.BooleanField(null=False, default=False)
    votes_to_skip: IntegerField = models.IntegerField(null=False, default=1)
    created_at: DateTimeField  = models.DateTimeField(auto_now_add=True)
