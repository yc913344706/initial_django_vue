"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path

urlpatterns = [
    path('admin/', admin.site.urls),

    re_path('^api/v1/demo/', include('apps.demo.urls')),
    re_path('^api/v1/auth/', include('apps.myAuth.urls')),
    re_path('^api/v1/user/', include('apps.user.urls')),
    re_path('^api/v1/perm/', include('apps.perm.urls')),
    re_path('^api/v1/audit/', include('apps.audit.urls')),
]
