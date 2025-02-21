from rest_framework.permissions import BasePermission

class IsPostAuthor(BasePermission):
    """
    Permission that allows only the author of a post to view or edit it.
    """
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user