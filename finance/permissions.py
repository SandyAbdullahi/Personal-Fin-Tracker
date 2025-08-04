from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Safe-methods (GET/HEAD/OPTIONS) are allowed if the object belongs
    to the request.user. Unsafe methods require ownership too.
    """

    def has_object_permission(self, request, view, obj):
        # Assumes every domain model has a `user` FK
        return obj.user == request.user
