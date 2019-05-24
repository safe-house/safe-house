from django.contrib import admin
from django.urls import path, include
from index import urls as index_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(index_urls))
]
