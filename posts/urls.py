from django.urls import path

from posts.feeds import LatestPostsFeed
from posts.views import PostListView, PostDetailView, SavedPostListView, RandomPostsView, DeletePostView, DeletePostCommentView

app_name = 'posts'

urlpatterns = [
    path('feed/', LatestPostsFeed(), name='feed'),  # RSS FEEDS
    path('search', PostListView.as_view(), name='search'),
    path('', PostListView.as_view(), name='index'),
    path('<slug:type_slug>/', PostListView.as_view(), name='type'),
    path('topic/<slug:topic_slug>/', PostListView.as_view(), name='topic'),
    path('tag/<slug:tag_slug>/', PostListView.as_view(), name='tag'),
    path('detail/<slug:post_slug>/', PostDetailView.as_view(), name='detail'),
    path('saves', SavedPostListView.as_view(), name='saves'),
    path('random', RandomPostsView.as_view(), name='random'),
    path('delete/<slug:post_slug>/', DeletePostView.as_view(), name='delete'),
    path('comments/delete/<int:id>/', DeletePostCommentView.as_view(),
         name='comment_delete'),
]
