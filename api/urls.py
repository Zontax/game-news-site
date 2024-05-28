from django.urls import path

from api.views import TestHtmxAPIView, DateTimeAPIView, DateTimeSecondsAPIView, SearchPostsAPIView, GetReplyCommentsAPIView, UserListAPIView, PostListAPIView, PostDetailAPIView, PostCreateAPIView, FakePostCreateAPIView, CheckUsernameAPIView, CheckEmailAPIView

app_name = 'api'

urlpatterns = [
    path('test/', TestHtmxAPIView.as_view(), name='test'),
    path('datetime/', DateTimeAPIView.as_view(), name='datetime'),
    path('datetime/seconds/', DateTimeSecondsAPIView.as_view(), name='seconds'),
    path('user-list/', UserListAPIView.as_view(), name='user_list'),
    path('search-posts/', SearchPostsAPIView.as_view(), name='search_posts'),
    path('get-reply-comments/<int:id>/', GetReplyCommentsAPIView.as_view(), name='get_reply_comments'),
    path('users/', UserListAPIView.as_view(), name='users'),
    path('posts/', PostListAPIView.as_view(), name='posts'),
    path('posts/<int:pk>/', PostDetailAPIView.as_view(), name='post_detail'),
    path('posts/create/', PostCreateAPIView.as_view(), name='post_create'),
    path('posts/fake/<int:count>/', FakePostCreateAPIView.as_view(), name='post_fake'),
    path('users/check_username/', CheckUsernameAPIView.as_view(), name='check_username'),
    path('users/check_email/', CheckEmailAPIView.as_view(), name='check_email'),
]
