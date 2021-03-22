from rest_framework import permissions


class CustomPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        pass
