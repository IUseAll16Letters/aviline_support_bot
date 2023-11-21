from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from config import settings

urlpatterns = [
    path('magic/', admin.site.urls),
] + (static(settings.STATIC_URL, document_root=settings.STATIC_ROOT))
