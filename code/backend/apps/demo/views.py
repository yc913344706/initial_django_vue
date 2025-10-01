from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
# Create your views here.

def index(request):
    return HttpResponse("Hello, world. You're at the demo index.")

def health_check(request):
    """Simple health check endpoint"""
    return JsonResponse({"status": "healthy", "service": "backend"}, status=200)
