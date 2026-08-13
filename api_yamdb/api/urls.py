from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet, CommentsViewSet, GenreViewSet,
    ReviewViewSet, TitleViewSet, UsersViewSet
)

v1_router = DefaultRouter()
v1_router.register('categories', CategoryViewSet, basename='categories')
v1_router.register('genres', GenreViewSet, basename='genres')
v1_router.register('titles', TitleViewSet, basename='titles')
v1_router.register('users', UsersViewSet, basename='users')

urlpatterns = [
    path(
        'v1/titles/<int:title_id>/reviews/',
        ReviewViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='reviews-list'
    ),
    path(
        'v1/titles/<int:title_id>/reviews/<int:pk>/',
        ReviewViewSet.as_view({
            'get': 'retrieve',
            'patch': 'partial_update',
            'delete': 'destroy'
        }),
        name='reviews-detail'
    ),
    path(
        'v1/titles/<int:title_id>/reviews/<int:review_id>/comments/',
        CommentsViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='comments-list'
    ),
    path(
        'v1/titles/<int:title_id>/reviews/<int:review_id>/comments/<int:pk>/',
        CommentsViewSet.as_view({
            'get': 'retrieve',
            'patch': 'partial_update',
            'delete': 'destroy'
        }),
        name='comments-detail'
    ),
    path('v1/', include(v1_router.urls)),
    path('v1/', include('users.urls'))
]