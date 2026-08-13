from rest_framework import filters, mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, FloatField
from django.db.models.functions import Coalesce

from reviews.filters import TitleFilter
from users.permissions import (
    IsAdmin, IsAdminOrModeratorOrOwnerOrReadOnly, IsAdminOrReadOnly
)
from reviews.models import Category, Comments, Genre, Review, Title
from .serializers import (
    CategorySerializer,
    CommentsSerializer,
    GenreSerializer,
    ReviewSerializer,
    UserMeSerializer,
    TitleReadSerializer,
    TitleWriteSerializer,
    UserSerializer
)

User = get_user_model()


class CategoryGenreBaseViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """
    Базовый класс для категорий и жанров.
    """

    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    permission_classes = (IsAdminOrReadOnly,)


class CategoryViewSet(CategoryGenreBaseViewSet):
    """
    Вьюсет для управления категориями.
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CategoryGenreBaseViewSet):
    """
    Вьюсет для управления жанрами.
    """

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для управления произведениями.
    """

    queryset = Title.objects.annotate(
        rating=Coalesce(Avg('reviews__score'), None,
                        output_field=FloatField())
    ).all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    permission_classes = (IsAdminOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete', 'head', 'options')

    def get_serializer_class(self):
        """Выбирает сериализатор в зависимости от типа запроса."""
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer


class UsersViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для управления пользователями.
    """

    http_method_names = ('get', 'post', 'patch', 'delete', 'head', 'options')

    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'

    @action(detail=False,
            methods=['get', 'patch'],
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        """Получение и изменение данных своей учетной записи."""
        user = request.user
        if request.method == 'GET':
            serializer = UserMeSerializer(user)
            return Response(serializer.data)

        serializer = UserMeSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


class ReviewViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для управления отзывами.
    """

    serializer_class = ReviewSerializer
    permission_classes = (IsAdminOrModeratorOrOwnerOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete', 'head', 'options')

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return Review.objects.filter(title=title).select_related('author')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentsViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для управления комментариями.
    """

    serializer_class = CommentsSerializer
    permission_classes = (IsAdminOrModeratorOrOwnerOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete', 'head', 'options')

    def get_review(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return get_object_or_404(Review, title=title,
                                 pk=self.kwargs.get('review_id'))

    def get_queryset(self):
        review = self.get_review()
        return Comments.objects.filter(review=review).select_related('author')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
