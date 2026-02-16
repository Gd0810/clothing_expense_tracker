from django.urls import path
from . import views

urlpatterns = [
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/create/', views.expense_create, name='expense_create'),
    path('incomes/', views.income_list, name='income_list'),
    path('incomes/create/', views.income_create, name='income_create'),
]