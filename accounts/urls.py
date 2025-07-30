from django.urls import path
from .views import login_view

urlpatterns = [
    path('api/auth/login/', login_view, name='login'),
]