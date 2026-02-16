from django.urls import path
from . import views

urlpatterns = [
    path('', views.shop_list, name='shop_list'),
    path('create/', views.shop_create, name='shop_create'),
]