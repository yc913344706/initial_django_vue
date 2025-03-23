from django.shortcuts import render
from django.http import HttpResponse
from lib.request_tool import pub_success_response
# Create your views here.

def index(request):
    return HttpResponse("Hello, world. You're at the auth index.")

def login(request):
    data = {
        "avatar": "https://img.yzcdn.cn/vant/ipad.png",
        "username": "admin",
        "nickname": "admin",
        "roles": ["admin"],
        "permissions": ["admin"],
        "accessToken": "1234567890",
        "refreshToken": "1234567890",
        "expires": "2026-03-23 12:00:00"
    }
    return pub_success_response(data=data)

def refresh_token(request):
    return pub_success_response(data={"token": "1234567890"})
