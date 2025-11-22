from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('refresh-token/', views.refresh_token, name='refresh_token'),
    path('verify-access-token/', views.verify_access_token, name='verify_access_token'),
    path("get-async-routes/", views.get_async_routes, name="get_async_routes"),
] 