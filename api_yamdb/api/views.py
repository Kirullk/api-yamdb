from rest_framework import filters, mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, FloatField
from django.db.models.functions import Coalesce
from django.core.mail import send_mail
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView

from .filters import TitleFilter
from .permissions import (
    IsAdmin, IsAdminOrModeratorOrOwnerOrReadOnly, IsAdminOrReadOnly
)
from reviews.models import Category, Comments, Genre, Review, Title
from . import serializers
from .utils import generate_confirmation_code


User = get_user_model()


class SignUpView(APIView):
    """
    Регистрация нового пользователя или повторная отправка кода подтверждения.

    Принимает POST-запрос с username и email.
    Если пользователь с таким username уже существует и email совпадает —
    отправляет новый код подтверждения на email.
    Если username свободен, но email занят — возвращает ошибку.
    Если всё свободно — создаёт нового пользователя и отправляет код.
    """

    permission_classes = []

    def post(self, request):
        serializer = serializers.SignUpSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data['username']
        email = serializer.validated_data['email']

        user_by_username = User.objects.filter(username=username).first()
        if user_by_username:
            if user_by_username.email != email:
                return Response(
                    {'email': 'Неверный email для данного пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            confirmation_code = generate_confirmation_code()
            user_by_username.confirmation_code = confirmation_code
            user_by_username.save()

            send_mail(
                subject='Код подтверждения YaMDb',
                message=f'Ваш код подтверждения: {confirmation_code}',
                from_email=None,
                recipient_list=[email],
                fail_silently=True,
            )

            return Response(
                {'email': email, 'username': username},
                status=status.HTTP_200_OK
            )

        if User.objects.filter(email=email).exists():
            return Response(
                {'email': 'Пользователь с таким email уже существует'},
                status=status.HTTP_400_BAD_REQUEST
            )

        confirmation_code = generate_confirmation_code()
        user = User.objects.create(username=username, email=email)
        user.confirmation_code = confirmation_code
        user.save()

        send_mail(
            subject='Код подтверждения YaMDb',
            message=f'Ваш код подтверждения: {confirmation_code}',
            from_email=None,
            recipient_list=[email],
            fail_silently=True,
        )

        return Response(
            {'email': email, 'username': username},
            status=status.HTTP_200_OK
        )


class TokenView(APIView):
    """
    Получение JWT-токена в обмен на username и confirmation_code.

    Принимает POST-запрос с username и confirmation_code.
    Если пользователь найден и код подтверждения верный — возвращает JWT-токен.
    """

    permission_classes = ()

    def post(self, request):
        serializer = serializers.TokenSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data['username']
        confirmation_code = serializer.validated_data['confirmation_code']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {'error': 'Пользователь не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        if user.confirmation_code != confirmation_code:
            return Response(
                {'error': 'Неверный код подтверждения'},
                status=status.HTTP_400_BAD_REQUEST
            )

        refresh = RefreshToken.for_user(user)
        return Response(
            {'token': str(refresh.access_token)},
            status=status.HTTP_200_OK
        )


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
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
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

    serializer_class = serializers.UserSerializer
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
            serializer = serializers.UserMeSerializer(user)
            return Response(serializer.data)

        serializer = serializers.UserMeSerializer(user, data=request.data,
                                                  partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


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
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return Review.objects.filter(title=title).select_related('author')

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
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return get_object_or_404(Review, title=title,
                                 pk=self.kwargs.get('review_id'))

    def get_queryset(self):
        review = self.get_review()
        return Comments.objects.filter(review=review).select_related('author')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
