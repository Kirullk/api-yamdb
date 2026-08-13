from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from .views import (
    CategoryViewSet, CommentsViewSet, GenreViewSet,
    ReviewViewSet, TitleViewSet, UsersViewSet
)

v1_router = DefaultRouter()
v1_router.register('categories', CategoryViewSet, basename='categories')
v1_router.register('genres', GenreViewSet, basename='genres')
v1_router.register('titles', TitleViewSet, basename='titles')
v1_router.register('users', UsersViewSet, basename='users')

reviews_router = routers.NestedDefaultRouter(
    v1_router, 'titles', lookup='title'
)
reviews_router.register('reviews', ReviewViewSet, basename='reviews')

comments_router = routers.NestedDefaultRouter(
    reviews_router, 'reviews', lookup='review'
)
comments_router.register('comments', CommentsViewSet, basename='comments')

urlpatterns = [
    path('v1/', include(v1_router.urls)),
    path('v1/', include(reviews_router.urls)),
    path('v1/', include(comments_router.urls)),
    path('v1/', include('users.urls'))
]
