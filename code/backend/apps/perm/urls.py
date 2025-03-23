from django.urls import path
from . import views

urlpatterns = [
    # Permission URLs
    path('permissions/', views.permission_list, name='permission_list'),
    path('permission/', views.permission, name='permission'),
    
    # Role URLs
    path('roles/', views.role_list, name='role_list'),
    path('role/', views.role, name='role'),
] 