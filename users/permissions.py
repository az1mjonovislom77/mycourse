from rest_framework import permissions

class IsAuthenticated(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

class IsActiveUser(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_active

class IsAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff
