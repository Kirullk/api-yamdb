from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import SignUpSerializer, TokenSerializer
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
        serializer = SignUpSerializer(data=request.data)
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

    permission_classes = []

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
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
