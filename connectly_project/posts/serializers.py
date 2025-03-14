from rest_framework import serializers
from .models import User, Post, Like, Comment

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'created_at']

class PostSerializer(serializers.ModelSerializer):
    comments = serializers.StringRelatedField(many=True, read_only=True)
    likes = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'content', 'author', 'created_at', 'comments', 'likes']

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'created_at']

    def validate_user(self, value):
        if not User.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("User not found.")
        return value

    def validate_post(self, value):
        if not Post.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Post not found.")
        return value

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'text', 'author', 'post', 'created_at']

    def validate_author(self, value):
        if not User.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Author not found.")
        return value

    def validate_post(self, value):
        if not Post.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Post not found.")
        return value