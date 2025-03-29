from django.urls import path
from . import views

urlpatterns = [
    path('audit-logs/', views.get_audit_logs, name='get_audit_logs'),
] 