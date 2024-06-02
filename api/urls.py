from django.urls import path

from api import views
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

app_name = 'api'

urlpatterns = [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(), name='docs'),

    path('ip/', views.IP_APIView.as_view(), name='ip_address'),
    path('datetime/', views.ServerDateTimeAPIView.as_view(), name='datetime'),
    path('client-datetime/', views.DateTimeAPIView.as_view(), name='client_datetime'),
    path('datetime/seconds/', views.DateTimeSecondsAPIView.as_view(), name='seconds'),
    path('user-list/', views.UserListAPIView.as_view(), name='user_list'),
    path('search-posts/', views.SearchPostsAPIView.as_view(), name='search_posts'),
    path('get-reply-comments/<int:id>/', views.GetReplyCommentsAPIView.as_view(),
         name='get_reply_comments'),
    path('users/', views.UserListAPIView.as_view(), name='users'),
    path('posts/', views.PostListAPIView.as_view(), name='posts'),
    path('posts/<int:pk>/', views.PostDetailAPIView.as_view(), name='post_detail'),
    path('posts/create/', views.PostCreateAPIView.as_view(), name='post_create'),
    path('posts/fake/<int:count>/', views.FakePostCreateAPIView.as_view(),
         name='post_fake'),
    path('users/check_username/', views.CheckUsernameAPIView.as_view(),
         name='check_username'),
    path('users/check_email/', views.CheckEmailAPIView.as_view(), name='check_email'),

    # HTMX
    path('test/', views.TestHtmxAPIView.as_view(), name='htmx_test'),
    path('htmx-modal/', views.ModalWindowAPIView.as_view(), name='htmx_modal'),
]
