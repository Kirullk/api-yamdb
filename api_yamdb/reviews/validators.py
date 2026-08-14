import datetime

from rest_framework import serializers


def validate_year(value):
    """Проверяет, что год выпуска произведения не больше текущего."""
    current_year = datetime.date.today().year
    if value > current_year:
        raise serializers.ValidationError(
            'Год выпуска не может быть больше текущего!'
        )
    return value
