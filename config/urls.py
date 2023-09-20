from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('magic/', admin.site.urls),
]
