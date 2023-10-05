from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_year(value):
    """Проверка года выпуска. Он не должен быть больше текущего."""
    if value > timezone.now().year:
        raise ValidationError('Год выпуска не может быть больше текущего')
    return value
