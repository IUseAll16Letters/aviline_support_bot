from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from config import settings
from aviline.views import LogView


urlpatterns = [
    path('magic/', admin.site.urls),
    path('check_logs_view/', LogView.as_view(), name='logs'),
] + (static(settings.STATIC_URL, document_root=settings.STATIC_ROOT))
