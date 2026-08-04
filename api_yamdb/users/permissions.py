from rest_framework import permissions


# Права доступа для работы с пользователями.
class IsAdmin(permissions.BasePermission):
    """Разрешение только для администраторов и суперюзеров."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role == 'admin' or request.user.is_superuser
        )


# Права доступа для жанров, категорий, произведений.
class IsAdminOrReadOnly(permissions.BasePermission):
    """
    - GET, HEAD, OPTIONS — доступны всем (включая анонимов)
    - POST, PUT, PATCH, DELETE — только администраторам.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and (
            request.user.role == 'admin' or request.user.is_superuser
        )


# Права доступа для отзывов и комментариев.
class IsAdminOrModeratorOrOwnerOrReadOnly(permissions.BasePermission):
    """
    - GET, HEAD, OPTIONS — доступны всем (включая анонимов)
    - POST — только авторизованным
    - PUT, PATCH, DELETE — автору, модератору или администратору.
    """
    def has_permission(self, request, view):
        return (request.user.is_authenticated
                or request.method in permissions.SAFE_METHODS)

    def has_object_permission(self, request, view, obj):
        role = request.user.role
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or role in ('moderator', 'admin')
            or request.user.is_superuser
        )
# Для анонимов используйте IsAuthenticatedOrReadOnly.
