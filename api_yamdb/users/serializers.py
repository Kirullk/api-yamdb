import re

from rest_framework import serializers
from django.contrib.auth import get_user_model


User = get_user_model()


class SignUpSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(max_length=254)

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Выберите другое имя пользователя'
            )
        if not re.match(r'^[\w.@+-]+\Z', value):
            raise serializers.ValidationError('Недопустимые символы')
        return value


class TokenSerializer(serializers.Serializer):
    """
    Сериализатор для работы с токеном.
    """

    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField()
