from rest_framework.permissions import BasePermission

class IsPostAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
    
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'ADMIN'

class IsEditorOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ['EDITOR', 'ADMIN']

class IsOwnerOrEditorOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role in ['ADMIN', 'EDITOR']:
            return True
        return obj.author == request.user
    
class IsOwnerOrFriend(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.privacy == 'PUBLIC':
            return True
        if obj.privacy == 'FRIENDS':
            return request.user in obj.author.friends.all()
        return obj.author == request.user

class CanViewPrivatePost(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('posts.view_private_post')  # For admins/moderators