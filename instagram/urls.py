from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('apps.base.urls')),
    path('profile/', include('apps.account.urls')),
    path('explore/', include('apps.explore.urls')),
    path('direct/', include('apps.direct.urls')),

    path('api-auth/', include('api.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
