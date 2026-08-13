import re
from django.contrib.auth import get_user_model
from rest_framework import serializers

import datetime
from reviews.models import Category, Comments, Genre, Review, Title


User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для категорий.
    """

    class Meta:

        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """
    Сериализатор для жанров.
    """

    class Meta:

        model = Genre
        fields = ('name', 'slug')


class TitleReadSerializer(serializers.ModelSerializer):
    """
    Сериализатор для чтения произведений.
    """

    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True)
    rating = serializers.FloatField(read_only=True, default=0)

    class Meta:

        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )


class TitleWriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания произведения.
    """

    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
        allow_empty=False
    )

    class Meta:

        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')

    def validate_year(self, value):
        """Проверка что год выпуска подходящий."""
        current_year = datetime.date.today().year
        if value > current_year:
            raise serializers.ValidationError(
                'Год выпуска не может быть больше текущего!'
            )
        return value


class ReviewSerializer(serializers.ModelSerializer):
    """
    Сериализатор отзывов.
    """

    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:

        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        read_only_fields = ('id', 'author', 'pub_date')

    def validate(self, attrs):
        """Запрещает второй отзыв пользователя на произведение."""
        if self.instance is not None:
            return attrs

        request = self.context.get('request')
        view = self.context.get('view')
        if request is None or view is None:
            return attrs

        if Review.objects.filter(
            title_id=view.kwargs.get('title_id'),
            author=request.user
        ).exists():
            raise serializers.ValidationError(
                'Пользователь уже оставил отзыв '
                'на это произведение.'
            )
        return attrs


class CommentsSerializer(serializers.ModelSerializer):
    """
    Сериализатор для комментариев.
    """
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:

        model = Comments
        fields = ('id', 'text', 'author', 'pub_date')
        read_only_fields = ('id', 'author', 'pub_date')


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для работы с пользователями.
    """

    class Meta:

        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')

    def validate_username(self, value):
        if not re.match(r'^[\w.@+-]+\Z', value):
            raise serializers.ValidationError(
                'Имя пользователя содержит недопустимые символы'
            )
        return value


class UserMeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для изменения учетной записи.
    Пользователь не может изменить свою роль.
    """

    class Meta:

        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')
        read_only_fields = ('role',)

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Выберите другое имя пользователя'
            )
        if not re.match(r'^[\w.@+-]+\Z', value):
            raise serializers.ValidationError(
                'Имя пользователя содержит недопустимые символы'
            )
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exclude(
            pk=self.instance.pk
        ).exists():
            raise serializers.ValidationError(
                'Пользователь с таким email уже существует'
            )
        return value
