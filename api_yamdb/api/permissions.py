from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Проверяем, является ли пользователь админом.
    Проверка не проводится для безопасных методов,
    таких как GET, HEAD и OPTIONS.
    """

    message = 'Действие недоступно для вас.'

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_admin
        )


class IsAuthorOrModeratorOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and (
                request.user.is_admin
                or request.user.is_moderator
                or request.user == obj.author
            )
        )


class IsModerator(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_moderator


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_admin or request.user.is_superuser
