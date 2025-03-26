from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate
from .models import Post, Comment, Like
from .serializers import UserSerializer, PostSerializer, CommentSerializer, LikeSerializer
from .permissions import IsPostAuthor, IsAdmin, IsEditorOrAdmin, IsOwnerOrEditorOrAdmin
from singletons.logger_singleton import LoggerSingleton
from factories.post_factory import PostFactory
from rest_framework.authtoken.models import Token
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.conf import settings

logger = LoggerSingleton().get_logger()
logger.info("API initialized successfully.")

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class UserListCreate(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        cache_key = 'all_users'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
            
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        cache.set(cache_key, serializer.data, timeout=CACHE_TTL)
        return Response(serializer.data)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.create_user(
                username=serializer.validated_data['username'],
                password=request.data.get('password'),
                email=serializer.validated_data.get('email')
            )
            cache.delete('all_users')
            return Response(
                UserSerializer(user).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PostListCreate(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAdmin]
    pagination_class = CustomPagination
    
    def get(self, request):
        cache_key = f'posts_{request.get_full_path()}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
            
        posts = Post.objects.all().order_by('-created_at')
        page = self.pagination_class().paginate_queryset(posts, request)
        serializer = PostSerializer(page, many=True, context={'request': request})
        response = self.pagination_class().get_paginated_response(serializer.data)
        cache.set(cache_key, response.data, timeout=CACHE_TTL)
        return response

    def post(self, request):
        serializer = PostSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            post = serializer.save(author=request.user)
            cache.delete_pattern('posts_*')
            cache.delete_pattern('newsfeed_*')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommentListCreate(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cache_key = f'comments_{request.get_full_path()}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
            
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True, context={'request': request})
        cache.set(cache_key, serializer.data, timeout=CACHE_TTL)
        return Response(serializer.data)

    def post(self, request):
        serializer = CommentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(author=request.user)
            cache.delete_pattern('comments_*')
            cache.delete_pattern('posts_*')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PostDetailView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrEditorOrAdmin]

    def get(self, request, pk):
        cache_key = f'post_{pk}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
            
        post = get_object_or_404(Post, pk=pk)
        self.check_object_permissions(request, post)
        serializer = PostSerializer(post, context={'request': request})
        cache.set(cache_key, serializer.data, timeout=CACHE_TTL)
        return Response(serializer.data)

    def delete(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        self.check_object_permissions(request, post)
        post.delete()
        cache.delete_pattern('posts_*')
        cache.delete_pattern('newsfeed_*')
        return Response(status=status.HTTP_204_NO_CONTENT)

class LikeListCreate(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cache_key = 'all_likes'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
            
        likes = Like.objects.all()
        serializer = LikeSerializer(likes, many=True, context={'request': request})
        cache.set(cache_key, serializer.data, timeout=CACHE_TTL)
        return Response(serializer.data)

    def post(self, request):
        serializer = LikeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            like, created = Like.objects.get_or_create(
                user=request.user,
                post=serializer.validated_data['post']
            )
            if not created:
                return Response(
                    {'message': 'You have already liked this post.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            cache.delete(f'post_{serializer.validated_data["post"].id}')
            cache.delete_pattern('posts_*')
            cache.delete('all_likes')
            return Response(
                LikeSerializer(like).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AssignRoleView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        serializer = UserSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            try:
                user = User.objects.get(username=serializer.validated_data['username'])
                group, created = Group.objects.get_or_create(name=request.data.get('role'))
                user.groups.add(group)
                cache.delete('all_users')
                return Response(
                    {"message": f"Role assigned to user '{user.username}'."},
                    status=status.HTTP_200_OK
                )
            except User.DoesNotExist:
                return Response(
                    {"error": "User not found."},
                    status=status.HTTP_404_NOT_FOUND
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class NewsfeedView(generics.ListAPIView):
    serializer_class = PostSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        cache_key = 'newsfeed_posts'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
            
        queryset = Post.objects.all().order_by('-created_at')
        cache.set(cache_key, queryset, timeout=CACHE_TTL)
        return queryset
    
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        
        # Privacy check
        if user.privacy_settings.profile_visibility == 'PRIVATE' and user != request.user:
            return Response({"error": "Profile is private"}, status=403)
        if user.privacy_settings.profile_visibility == 'FRIENDS' and not user.friends.filter(id=request.user.id).exists():
            return Response({"error": "Profile visible to friends only"}, status=403)
        
        serializer = UserSerializer(user)
        return Response(serializer.data)
    

class ProtectedView(APIView):
    """
    A simple protected view that requires authentication
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            'message': 'This is a protected view',
            'user': request.user.username
        }, status=status.HTTP_200_OK)