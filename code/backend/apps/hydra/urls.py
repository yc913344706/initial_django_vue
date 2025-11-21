from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.hydra_login, name='hydra_login'),
    path('consent/', views.hydra_consent, name='hydra_consent'),
    path('userinfo/', views.hydra_userinfo, name='hydra_userinfo'),
    path('logout/', views.hydra_logout, name='hydra_logout'),
    path('manage-client/', views.manage_oauth2_client, name='manage_oauth2_client'),
]