from django.urls import path
from . import views

urlpatterns = [
    # User URLs
    path('users/', views.user_list, name='user_list'),
    path('user/', views.user, name='user'),
    path('groups/', views.user_group_list, name='user_group_list'),
    path('group/', views.user_group, name='user_group'),
    path('change-password/', views.change_password, name='change_password'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('password-config/', views.password_config, name='password_config'),
] 