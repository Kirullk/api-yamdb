import datetime
import re

from django.core.exceptions import ValidationError

from .constants import RESERVED_USERNAMES, USERNAME_PATTERN


def validate_username(value):
    """
    Единая валидация для имени пользователя.
    """
    if value.lower() in RESERVED_USERNAMES:
        raise ValidationError(
            f'Имя пользователя "{value}" запрещено. Выберите другое имя.'
        )

    forbidden_chars = re.sub(USERNAME_PATTERN, '', value)

    if forbidden_chars:
        unique_forbidden = sorted(set(forbidden_chars))
        forbidden_str = ' '.join(repr(ch) for ch in unique_forbidden)

        raise ValidationError(
            f'Имя пользователя содержит запрещённые символы: {forbidden_str}. '
            f'Разрешены: латинские буквы, цифры, точка (.), дефис (-), '
            f'подчёркивание (_), символы @ и +.'
        )
    return value


def validate_year(value):
    """Проверяет, что год выпуска произведения не больше текущего."""
    current_year = datetime.date.today().year
    if value > current_year:
        raise ValidationError(
            'Год выпуска не может быть больше текущего!'
        )
    return value
