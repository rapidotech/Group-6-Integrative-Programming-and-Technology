from django.urls import path
from .views import UserListCreate, PostListCreate, LikeListCreate, CommentListCreate
from .views import follow_user, unfollow_user
from .views import NewsFeedView

urlpatterns = [
    path('users/', UserListCreate.as_view(), name='user-list-create'),
    path('posts/', PostListCreate.as_view(), name='post-list-create'),
    path('likes/', LikeListCreate.as_view(), name='like-list-create'),
    path('comments/', CommentListCreate.as_view(), name='comment-list-create'),
    path('users/<int:user_id>/follow/', follow_user, name='follow_user'),
    path('users/<int:user_id>/unfollow/', unfollow_user, name='unfollow_user'),
    path('posts/newsfeed/', NewsFeedView.as_view(), name='newsfeed'), 
]