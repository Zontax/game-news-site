from django.contrib import admin
from django.conf.urls.static import static
from django.urls import include, path

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from filebrowser.sites import site
from app import settings

urlpatterns = [
    # API
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='docs'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/', include('api.urls', namespace='api')),
    # URLS
    path('admin/filebrowser/', site.urls),
    path('admin/', admin.site.urls),
    path('', include('main.urls', namespace='main')),
    path('user/', include('users.urls', namespace='user')),
    path('posts/', include('posts.urls', namespace='posts')),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    # path('ckeditor/', include('ckeditor_uploader.urls')),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += [
        path('__debug__/', include('debug_toolbar.urls')),
    ]
