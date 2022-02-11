from .models import *
from django.shortcuts import render

def home(request):
    return render(request, './finance/home.html')