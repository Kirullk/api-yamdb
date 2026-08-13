import re

from django.core.exceptions import ValidationError

from .constants import (RESERVED_USERNAMES, USERNAME_MAX_LENGTH,
                        USERNAME_PATTERN)


def validate_username(value):
    """
    Единая валидация для имени пользователя.
    """
    if not value or len(value) > USERNAME_MAX_LENGTH:
        raise ValidationError(
            'Имя пользователя не может быть пустым и должно быть не длиннее '
            f'{USERNAME_MAX_LENGTH} символов.'
        )

    if value.lower() in RESERVED_USERNAMES:
        raise ValidationError(
            f'Имя пользователя "{value}" запрещено. Выберите другое имя.'
        )

    if not re.match(USERNAME_PATTERN, value):
        raise ValidationError(
            'Имя пользователя содержит недопустимые символы. '
            'Разрешены: латинские буквы, цифры, точка (.), дефис (-), '
            'подчёркивание (_), символы @ и +.'
        )
    return value
