from django.shortcuts import render
from django.http import HttpResponse
from lib.request_tool import pub_success_response
from mock.fake_data import fake_user_login_data_list, fake_async_routes, fake_refresh_token_data
# Create your views here.

def index(request):
    return HttpResponse("Hello, world. You're at the auth index.")

def login(request):
    return pub_success_response(data=fake_user_login_data_list[1])

def refresh_token(request):
    return pub_success_response(data=fake_refresh_token_data)

def get_async_routes(request):
    return pub_success_response(data=fake_async_routes)
