from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    Разрешение только для администраторов и суперюзеров.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    - GET, HEAD, OPTIONS — доступны всем (включая анонимов)
    - POST, PUT, PATCH, DELETE — только администраторам.
    """

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated and request.user.is_admin)


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
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated and (
                obj.author == request.user
                or request.user.is_moderator
                or request.user.is_admin
            ))
        )
