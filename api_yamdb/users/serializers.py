from rest_framework import serializers
from django.contrib.auth import get_user_model


User = get_user_model()


class SignUpSerializer(serializers.Serializer):
    """Сериализатор для регистрации пользователя."""

    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(max_length=254)

    def validate_username(self, value):
        if self.username.lower() == 'me':
            raise serializers.ValidationError(
                'Выберите другое имя пользователя'
            )
        return value

    def validate(self, data):
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError(
                {'username': 'Пользователь с таким username уже существует'}
            )
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError(
                {'email': 'Пользователь с таким email уже существует'}
            )
        return data


class TokenSerializer(serializers.Serializer):
    """Сериализатор для работы с токеном."""

    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        confirmation_code = data.get('confirmation_code')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {'username': 'Пользователь не найден'}
            )
        if user.confirmation_code != confirmation_code:
            raise serializers.ValidationError(
                {'confirmation_code': 'Неверный код подтверждения'}
            )
        # Сохраняю пользователя в validated_data,
        # чтобы не делать второй запрос.
        data['user'] = user
        return data
