from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserCustomViewSet, PostViewSet

router = DefaultRouter()
router.register(r'users', UserCustomViewSet)
router.register(r'posts', PostViewSet)

urlpatterns = [
    path('', include(router.urls)),
]