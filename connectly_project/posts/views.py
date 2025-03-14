from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User, Post, Like, Comment
from .serializers import UserSerializer, PostSerializer, LikeSerializer, CommentSerializer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.pagination import PageNumberPagination


class UserListCreate(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PostListCreate(APIView):
    def get(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommentListCreate(APIView):
    def get(self, request):
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LikeListCreate(APIView):
    def get(self, request):
        likes = Like.objects.all()
        serializer = LikeSerializer(likes, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = LikeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommentListCreate(APIView):
    def get(self, request):
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@csrf_exempt
def follow_user(request, user_id):
    if request.method == 'POST':
        try:
            user_to_follow = User.objects.get(id=user_id)
            request.user.following.add(user_to_follow)
            return JsonResponse({'message': f'You are now following {user_to_follow.username}'}, status=200)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)

@csrf_exempt
def unfollow_user(request, user_id):
    if request.method == 'POST':
        try:
            user_to_unfollow = User.objects.get(id=user_id)
            request.user.following.remove(user_to_unfollow)
            return JsonResponse({'message': f'You have unfollowed {user_to_unfollow.username}'}, status=200)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        

class NewsFeedView(APIView):
    pagination_class = PageNumberPagination
    page_size = 10  # Set your desired page size

    def get(self, request):
        paginator = self.pagination_class()
        paginator.page_size = self.page_size
        posts = Post.objects.all().order_by('-created_at')
        result_page = paginator.paginate_queryset(posts, request)
        serializer = PostSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)