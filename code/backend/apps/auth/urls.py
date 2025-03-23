from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login, name="login"),
    path("refresh-token", views.refresh_token, name="refresh_token"),
]
