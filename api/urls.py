from django.urls import path

from api.views import TestHtmxAPIView, DateTimeAPIView, SearchPostsAPIView, GetReplyCommentsAPIView, PostLikeAPIView, PostDislikeAPIView, PostSaveAPIView, UserListAPIView, PostListAPIView, PostDetailAPIView, PostCreateAPIView, FakePostCreateAPIView

app_name = 'api'

urlpatterns = [
    path('test/', TestHtmxAPIView.as_view(), name='test'),
    path('datetime/', DateTimeAPIView.as_view(), name='datetime'),
    path('user-list/', UserListAPIView.as_view(), name='user_list'),
    path('search-posts/', SearchPostsAPIView.as_view(), name='search_posts'),
    path('get-reply-comments/<int:id>/', GetReplyCommentsAPIView.as_view(), name='get_reply_comments'),
    path('post-like/<int:post_id>/', PostLikeAPIView.as_view(), name='post_like'),
    path('post-dislike/<int:post_id>/', PostDislikeAPIView.as_view(), name='post_dislike'),
    path('post-save/<int:post_id>/', PostSaveAPIView.as_view(), name='post_save'),
    
    path('users/', UserListAPIView.as_view(), name='users'),
    path('posts/', PostListAPIView.as_view(), name='posts'),
    path('posts/<int:pk>/', PostDetailAPIView.as_view(), name='post_detail'),
    path('posts/create/', PostCreateAPIView.as_view(), name='post_create'),
    path('posts/fake/<int:count>/', FakePostCreateAPIView.as_view(), name='post_fake'),
]
