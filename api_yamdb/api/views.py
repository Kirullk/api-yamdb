from django.db.models import Avg, FloatField
from django.db.models.functions import Coalesce
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import serializers
from .filters import TitleFilter
from .permissions import (
    IsAdmin,
    IsAdminOrModeratorOrOwnerOrReadOnly,
    IsAdminOrReadOnly,
)
from reviews.models import (
    Category,
    Genre,
    Review,
    Title
)
from . import serializers


User = get_user_model()


class SignUpView(APIView):
    """
    Регистрация нового пользователя.
    """

    permission_classes = ()

    def post(self, request):
        serializer = serializers.SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenView(APIView):
    """
    Получение JWT-токена.
    """

    permission_classes = ()

    def post(self, request):
        serializer = serializers.TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


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
    serializer_class = serializers.CategorySerializer


class GenreViewSet(CategoryGenreBaseViewSet):
    """
    Вьюсет для управления жанрами.
    """

    queryset = Genre.objects.all()
    serializer_class = serializers.GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для управления произведениями.
    """

    queryset = Title.objects.annotate(
        rating=Coalesce(Avg('reviews__score'), None,
                        output_field=FloatField())
    ).all()
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = TitleFilter
    ordering_fields = ('name', 'year', 'rating')
    ordering = ('name',)
    permission_classes = (IsAdminOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete', 'head', 'options')

    def get_serializer_class(self):
        """Выбирает сериализатор в зависимости от типа запроса."""
        if self.action in ('list', 'retrieve'):
            return serializers.TitleReadSerializer
        return serializers.TitleWriteSerializer


class UsersViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для управления пользователями.
    """

    http_method_names = ('get', 'post', 'patch', 'delete', 'head', 'options')

    serializer_class = serializers.UserAdminSerializer
    queryset = User.objects.all()
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        """Получение данных своей учетной записи."""
        serializer = serializers.UserMeSerializer(request.user)
        return Response(serializer.data)

    @me.mapping.patch
    def me_patch(self, request):
        """Изменение данных своей учетной записи."""
        serializer = serializers.UserMeSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для управления отзывами.
    """

    serializer_class = serializers.ReviewSerializer
    permission_classes = (IsAdminOrModeratorOrOwnerOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete', 'head', 'options')

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.select_related('author')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentsViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для управления комментариями.
    """

    serializer_class = serializers.CommentsSerializer
    permission_classes = (IsAdminOrModeratorOrOwnerOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete', 'head', 'options')

    def get_review(self):
        return get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id'),
            title_id=self.kwargs.get('title_id'),
        )

    def get_queryset(self):
        return self.get_review().comments.select_related('author')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
