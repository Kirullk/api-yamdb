from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView

from .utils import generate_confirmation_code
from .serializers import SignUpSerializer, TokenSerializer


User = get_user_model()


class SignUpView(APIView):

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        username = serializer.validated_data['username']
        email = serializer.validated_data['email']
        confirmation_code = generate_confirmation_code()

        user = User.objects.create(username=username, email=email)
        user.confirmation_code = confirmation_code
        user.save()

        send_mail(
            subject='Код подтверждения YaMDb.',
            message=f'Ваш код подтверждения: {confirmation_code}',
            from_email=None,
            recipient_list=[email],
            fail_silently=True,
        )

        return Response({'email': email, 'username': username},
                        status=status.HTTP_200_OK)


class TokenView(APIView):

    def post(self, request):
        serializer = TokenSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(serializer.validated_data['user'])
        return Response({'token': str(refresh.access_token)},
                        status=status.HTTP_200_OK)
