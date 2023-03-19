from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('base.urls')),
<<<<<<< HEAD
    path('direct/inbox/', include('inbox.urls')),
=======
    path('profile/', include('account.urls')),
    path('explore/', include('explore.urls')),
    path('direct/', include('direct.urls')),

    path('api-auth/', include('api.urls')),

>>>>>>> tmp
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
