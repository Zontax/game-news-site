from django.urls import path

from posts.feeds import LatestPostsFeed
from posts import views
app_name = 'posts'

urlpatterns = [
    path('feed/', LatestPostsFeed(), name='feed'),
    path('search', views.PostListView.as_view(), name='search'),
    path('', views.PostListView.as_view(), name='index'),
    path('scroll/', views.ScrollPostListView.as_view(), 
         name='scroll'),
    path('<slug:type_slug>/', views.PostListView.as_view(), 
         name='type'),
    path('topic/<slug:topic_slug>/', views.PostListView.as_view(), 
         name='topic'),
    path('tag/<slug:tag_slug>/', views.PostListView.as_view(), 
         name='tag'),
    path('detail/<slug:post_slug>/', views.PostDetailView.as_view(), 
         name='detail'),
    path('saves', views.SavedPostListView.as_view(), 
         name='saves'),
    path('random', views.RandomPostsView.as_view(), 
         name='random'),
    path('delete/<slug:post_slug>/', views.DeletePostView.as_view(), 
         name='delete'),
    path('comments/delete/<int:id>/', views.DeletePostCommentView.as_view(),
         name='comment_delete'),
    path('like/<int:post_id>/', views.PostLikeAPIView.as_view(),
         name='post_like'),
    path('dislike/<int:post_id>/', views.PostDislikeAPIView.as_view(),
         name='post_dislike'),
    path('save/<int:post_id>/', views.PostSaveAPIView.as_view(),
         name='post_like'),
]
