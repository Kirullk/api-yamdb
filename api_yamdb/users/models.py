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

    class Role(models.TextChoices):
        USER = 'user', 'Пользователь'
        MODERATOR = 'moderator', 'Модератор'
        ADMIN = 'admin', 'Администратор'
    username = models.CharField(
        'Имя пользователя',
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        validators=(validate_username,)
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
        max_length=max(len(role[0]) for role in Role.choices),
        choices=Role.choices,
        default=Role.USER
    )
    confirmation_code = models.CharField(
        max_length=CONFIRMATION_CODE_LENGTH,
        blank=True
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return (self.role == self.Role.ADMIN
                or self.is_superuser
                or self.is_staff)

    @property
    def is_moderator(self):
        return self.role == self.Role.MODERATOR
