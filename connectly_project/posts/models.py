from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.conf import settings
from django.contrib.auth.hashers import make_password

class User(AbstractUser):
    # Temporary nullable fields to allow migration
    password = models.CharField(max_length=128, null=True, blank=True)
    last_login = models.DateTimeField(null=True, blank=True)
    app_label = 'posts' 
    
    ROLES = (
        ('ADMIN', 'Administrator'),
        ('EDITOR', 'Editor'),
        ('VIEWER', 'Viewer'),
        ('USER', 'Regular User'),
    )
    role = models.CharField(max_length=20, choices=ROLES, default='USER')
    
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        related_name='custom_user_groups',
        related_query_name='custom_user_group'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        related_name='custom_user_permissions',
        related_query_name='custom_user_permission'
    )

class PrivacySettings(models.Model):
    PRIVACY_CHOICES = [
        ('PUBLIC', 'Public - Visible to everyone'),
        ('FRIENDS', 'Friends - Visible to connections only'),
        ('PRIVATE', 'Private - Visible only to me'),
    ]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profile_visibility = models.CharField(max_length=10, choices=PRIVACY_CHOICES, default='PUBLIC')
    post_default = models.CharField(max_length=10, choices=PRIVACY_CHOICES, default='PUBLIC')

    def __str__(self):
        return f"Privacy settings for {self.user.username}"

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    privacy = models.CharField(max_length=10, choices=PrivacySettings.PRIVACY_CHOICES, default='PUBLIC')

    def __str__(self):
        return self.title
        
    class Meta:
        permissions = [
            ("view_private_post", "Can view private posts"),
        ]

class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='comments', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"

class Like(models.Model):
    post = models.ForeignKey(Post, related_name='likes', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')

    def __str__(self):
        return f"{self.user.username} likes {self.post.title}"

class Friendship(models.Model):
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name='friendships_initiated',
        on_delete=models.CASCADE
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name='friendships_received',
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('from_user', 'to_user')
        verbose_name_plural = 'friendships'

    def __str__(self):
        return f"{self.from_user} → {self.to_user} ({'accepted' if self.accepted else 'pending'})"