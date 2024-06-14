from django.contrib.sitemaps.views import sitemap
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from filebrowser.sites import site
from posts.sitemaps import PostSitemap
from app.settings import base


urlpatterns = [
    # API
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='docs'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/', include('api.urls', namespace='api')),
    # SITEMAPS
    path('sitemap.xml', sitemap, {'sitemaps': {'posts': PostSitemap}},
         name='django.contrib.sitemaps.views.sitemap'),
    # URLS
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('admin/filebrowser/', site.urls),
    path('admin/', admin.site.urls),
    path('', include('main.urls', namespace='main')),
    path('user/', include('users.urls', namespace='user')),
    path('posts/', include('posts.urls', namespace='posts')),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
]

if settings.DEBUG:
    urlpatterns += [
        path('__debug__/', include('debug_toolbar.urls')),
    ]
    urlpatterns += static(base.STATIC_URL,
                          document_root=base.STATIC_ROOT)
    urlpatterns += static(base.MEDIA_URL,
                          document_root=base.MEDIA_ROOT)
