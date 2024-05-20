from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.views.decorators.cache import cache_page

from main.views import IndexView, AboutView, TestEmailView

app_name = 'main'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('about', AboutView.as_view(), name='about'),
    path('test-email', TestEmailView.as_view(), name='test_email'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
