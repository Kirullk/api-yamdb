from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .constants import EMAIL_MAX_LENGTH, USERNAME_MAX_LENGTH
from .mixins import UsernameMixin
from .utils import generate_confirmation_code
from api_yamdb.settings import DEFAULT_FROM_EMAIL
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


class UserAdminSerializer(serializers.ModelSerializer, UsernameMixin):
    """
    Сериализатор для работы с пользователями.
    """

    class Meta:

        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')


class UserMeSerializer(UserAdminSerializer):
    """
    Сериализатор для изменения учетной записи.

    Пользователь не может изменить свою роль.
    """

    class Meta(UserAdminSerializer.Meta):
        read_only_fields = ('role',)


class SignUpSerializer(serializers.Serializer, UsernameMixin):
    """
    Сериализатор для работы с регистрацией.
    """

    username = serializers.CharField(max_length=USERNAME_MAX_LENGTH,
                                     validators=[validate_username])
    email = serializers.EmailField(max_length=EMAIL_MAX_LENGTH)

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')

        user_by_username = User.objects.filter(username=username).first()

        if user_by_username:
            if user_by_username.email != email:
                raise serializers.ValidationError(
                    {'email': 'Неверный email для данного пользователя'}
                )
            data['existing_user'] = user_by_username
            return data

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {'email': 'Пользователь с таким email уже существует'}
            )

        return data

    def create(self, validated_data):
        username = validated_data['username']
        email = validated_data['email']
        existing_user = validated_data.get('existing_user')

        if existing_user:
            confirmation_code = generate_confirmation_code()
            existing_user.confirmation_code = confirmation_code
            existing_user.save()
            user = existing_user
        else:
            confirmation_code = generate_confirmation_code()
            user = User.objects.create(username=username, email=email)
            user.confirmation_code = confirmation_code
            user.save()

        send_mail(
            subject='Код подтверждения YaMDb',
            message=f'Ваш код подтверждения: {confirmation_code}',
            from_email=DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=True,
        )

        return {'username': username, 'email': email}


class TokenSerializer(serializers.Serializer):
    """
    Сериализатор для работы с токеном.
    """

    username = serializers.CharField(max_length=USERNAME_MAX_LENGTH)
    confirmation_code = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        confirmation_code = data.get('confirmation_code')

        user = get_object_or_404(User, username=username)
        if user.confirmation_code != confirmation_code:
            raise serializers.ValidationError(
                {'error': 'Неверный код подтверждения'}
            )
        data['user'] = user
        return data

    def to_representation(self, instance):
        refresh = RefreshToken.for_user(instance)
        return {'token': str(refresh.access_token)}
