from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('profile/', views.profile, name='profile'),
    path('profile/update/',views.profile_update, name='profile_update'),
    path('logout/', views.logout_view, name='logout'),
]