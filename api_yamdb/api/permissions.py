from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    Разрешение только для администраторов и суперюзеров.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role == 'admin' or request.user.is_superuser
        )


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
        if request.method in permissions.SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            return False
        return (
            obj.author == request.user
            or request.user.role in ('moderator', 'admin')
            or request.user.is_superuser
        )
