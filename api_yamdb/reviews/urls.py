from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . views import CategoryViewSet, GenreViewSet, TitleViewSet, UsersViewSet

v1_router = DefaultRouter()
v1_router.register('categories', CategoryViewSet, basename='categories')
v1_router.register('genres', GenreViewSet, basename='genres')
v1_router.register('titles', TitleViewSet, basename='titles')
v1_router.register('users', UsersViewSet, basename='users')

urlpatterns = [
    path('v1/', include(v1_router.urls)),
    path('v1/', include('users.urls'))
]
