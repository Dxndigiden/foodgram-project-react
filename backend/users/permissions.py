from rest_framework import permissions


class IsAdminOrAuthorOrReadOnly(permissions.BasePermission):
    """Доступ у автора или админа"""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user or request.user.is_superuser


class IsAdminOrCurrentUserOrReadOnly(permissions.BasePermission):
    """Доступ у текущего пользователя или админа"""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.id == request.user or request.user.is_superuser
