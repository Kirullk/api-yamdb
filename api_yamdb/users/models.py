from django.contrib.auth.models import AbstractUser
from django.db import models

from api.validators import validate_username
from api.constants import (CONFIRMATION_CODE_LENGTH,
                           EMAIL_MAX_LENGTH,
                           ROLE_MAX_LENGTH,
                           USERNAME_MAX_LENGTH)


class User(AbstractUser):
    """
    Кастомная модель пользователя с ролями.
    """

    ROLE_CHOICES = (
        ('user', 'Пользователь'),
        ('moderator', 'Модератор'),
        ('admin', 'Администратор'),
    )
    username = models.CharField(
        'Имя пользователя',
        max_length=USERNAME_MAX_LENGTH,
        unique=True
    )
    email = models.EmailField(
        'Email',
        max_length=EMAIL_MAX_LENGTH,
        unique=True
    )
    first_name = models.CharField(
        'Имя',
        max_length=USERNAME_MAX_LENGTH,
        blank=True
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=USERNAME_MAX_LENGTH,
        blank=True
    )
    bio = models.TextField(
        'Био',
        blank=True
    )
    role = models.CharField(
        'Роль',
        max_length=ROLE_MAX_LENGTH,
        choices=ROLE_CHOICES,
        default='user'
    )
    confirmation_code = models.CharField(
        max_length=CONFIRMATION_CODE_LENGTH,
        blank=True
    )

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        validate_username(self.username)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'пользователи'
        ordering = ('username',)
