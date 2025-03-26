from rest_framework import serializers
from django.contrib.auth.models import User, Group
from .models import Post, Comment, Like

class UserSerializer(serializers.ModelSerializer):
    groups = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=Group.objects.all()
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'groups', 'date_joined']
        extra_kwargs = {
            'password': {'write_only': True},
            'date_joined': {'read_only': True}
        }

    def create(self, validated_data):
        groups = validated_data.pop('groups', [])
        user = User.objects.create_user(**validated_data)
        for group_name in groups:
            group, _ = Group.objects.get_or_create(name=group_name)
            user.groups.add(group)
        return user

class PostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author', 'author_name', 'likes_count', 'created_at', 'author', 'privacy']
        read_only_fields = ['author', 'created_at']
        extra_kwargs = {}
    
        def create(self, validated_data):
            request = self.context.get('request')
            if request and hasattr(request.user, 'privacy_settings'):
                validated_data['privacy'] = request.user.privacy_settings.post_default
            return super().create(validated_data)

    def get_likes_count(self, obj):
        return obj.likes.count()

class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'text', 'author', 'author_name', 'post', 'created_at']
        read_only_fields = ['author', 'created_at']

    def validate_post(self, value):
        if not Post.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Post not found.")
        return value

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'created_at']
        read_only_fields = ['user', 'created_at']

