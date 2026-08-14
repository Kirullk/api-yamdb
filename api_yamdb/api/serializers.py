from django.contrib.auth import get_user_model
from rest_framework import serializers

from reviews.models import Category, Comments, Genre, Review, Title
from reviews.validators import validate_year
from .constants import EMAIL_MAX_LENGTH, USERNAME_MAX_LENGTH
from .validators import validate_username


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
    rating = serializers.FloatField(read_only=True, default=None)

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
    year = serializers.IntegerField(validators=[validate_year])

    class Meta:

        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')

    def to_representation(self, instance):
        """
        Возвращает сериализованные данные.
        """
        return TitleReadSerializer(instance, context=self.context).data


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
        """
        Запрещает второй отзыв пользователя на произведение.
        """
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
        return validate_username(value)


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
        return validate_username(value)

    def validate_email(self, value):
        if User.objects.filter(email=value).exclude(
            pk=self.instance.pk
        ).exists():
            raise serializers.ValidationError(
                'Пользователь с таким email уже существует'
            )
        return value


class SignUpSerializer(serializers.Serializer):
    """
    Сериализатор для работы с регистрацией.
    """

    username = serializers.CharField(max_length=USERNAME_MAX_LENGTH,
                                     validators=[validate_username])
    email = serializers.EmailField(max_length=EMAIL_MAX_LENGTH)


class TokenSerializer(serializers.Serializer):
    """
    Сериализатор для работы с токеном.
    """

    username = serializers.CharField(max_length=USERNAME_MAX_LENGTH)
    confirmation_code = serializers.CharField()
