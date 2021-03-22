from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UserViewSet

# Create a router and register our viewSets with it.
router = DefaultRouter()
router.register(r'user', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
]
