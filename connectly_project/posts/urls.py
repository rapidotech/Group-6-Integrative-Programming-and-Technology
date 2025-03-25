from django.urls import path
from .views import UserListCreate, PostListCreate, CommentListCreate, PostDetailView, ProtectedView, AssignRoleView, LikeListCreate

urlpatterns = [
    path('users/', UserListCreate.as_view(), name='user-list-create'),
    path('posts/', PostListCreate.as_view(), name='post-list-create'),
    path('comments/', CommentListCreate.as_view(), name='comment-list-create'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('protected/', ProtectedView.as_view(), name='protected-view'),
    path('assign-role/', AssignRoleView.as_view(), name='assign-role'),
    path('likes/', LikeListCreate.as_view(), name='like-list-create'),  # Add this line
]