from django.urls import path
from . import views

urlpatterns = [
    # User URLs
    path('users/', views.user_list, name='user_list'),
    path('user/', views.user, name='user'),
    path('user_groups/', views.user_group_list, name='user_group_list'),
    path('user_group/', views.user_group, name='user_group'),
] 