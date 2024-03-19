from rest_framework import permissions


class IsAdminOrAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated and (
                request.user.is_superuser or obj.author == request.user
                or request.method == 'POST'
            )
        ) or request.method in permissions.SAFE_METHODS
