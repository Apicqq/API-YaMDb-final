from django.contrib.auth.models import AbstractUser
from django.db import models

from users import const


class User(AbstractUser):
    ROLE_CHOICES = (
        (const.ROLE_ADMIN, 'Администратор'),
        (const.ROLE_MODERATOR, 'Модератор'),
        (const.ROLE_USER, 'Пользователь'),
    )
    email = models.EmailField(
        verbose_name='Адрес email',
        unique=True,
        help_text=('Обязательное поле.'),
        error_messages={
            'unique': (
                'Пользователь с таким адресом электронной почты '
                'уже существует.'
            )
        },
    )
    bio = models.TextField(
        verbose_name='Биография',
        blank=True,
    )
    role = models.CharField(
        verbose_name='Роль',
        max_length=const.MAX_LENGTH_FIELD,
        choices=ROLE_CHOICES,
        default=const.ROLE_USER,
    )

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == const.ROLE_ADMIN

    @property
    def is_moderator(self):
        return self.role == const.ROLE_MODERATOR
