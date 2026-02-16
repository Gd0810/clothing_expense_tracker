from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('download/<str:format_type>/', views.download_report, name='download_report'),
]