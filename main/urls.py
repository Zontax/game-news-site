from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from main import views

app_name = 'main'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('about', views.AboutView.as_view(), name='about'),
    path('test', views.TestFunctionsView.as_view(), name='test'),
    path('decode', views.DecodeTextView.as_view(), name='decode_text'),
    path('test-email', views.TestEmailView.as_view(), name='test_email'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
