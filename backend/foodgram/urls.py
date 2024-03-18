from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

api_patterns = [
    path('', include('recipes.urls')), 
    path('', include('users.urls')) 
]

urlpatterns = [
    path('admin/', admin.site.urls), 
    path('api/', include(api_patterns)), 
    path('api/', include('rest_framework.urls')) 
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
