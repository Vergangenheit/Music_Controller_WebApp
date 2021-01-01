from django.shortcuts import render
from django.http import HttpRequest

# Create your views here.
def index(request: HttpRequest, *args, **kwargs):
    return render(request, 'frontend/index.html')

