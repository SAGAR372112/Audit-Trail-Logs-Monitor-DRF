from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('logs.urls')),
    path('', include('accounts.urls')),
]
