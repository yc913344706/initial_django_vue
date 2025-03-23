from django.urls import path
from . import views

urlpatterns = [
    # User URLs
    path('users/', views.user_list, name='user_list'),
    path('user/', views.user, name='user'),
] 