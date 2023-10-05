from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from core.models import BaseNameSlugModel
from reviews import const
from reviews.validators import validate_year

User = get_user_model()


class Title(models.Model):
    """Модель произведения."""

    name = models.CharField(
        max_length=const.MAX_LENGTH_FIELD,
        verbose_name='Название произведения',
    )
    year = models.SmallIntegerField(
        verbose_name='Год выпуска',
        null=True,
        validators=(validate_year,)
    )
    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        verbose_name='Категория',
        blank=True,
        null=True,
    )
    genre = models.ManyToManyField(
        'Genre',
        through='GenreTitle',
        verbose_name='Жанр',
    )
    description = models.TextField(
        verbose_name='Описание произведения',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'произведения'
        default_related_name = '%(class)ss'
        ordering = ('name',)

    def __str__(self):
        return self.name[:const.MAX_STR_LENGTH]


class Category(BaseNameSlugModel):
    """Модель категории."""

    class Meta(BaseNameSlugModel.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'категории'


class Genre(BaseNameSlugModel):
    """Модель жанра."""

    class Meta(BaseNameSlugModel.Meta):
        verbose_name = 'Жанр'
        verbose_name_plural = 'жанры'


class GenreTitle(models.Model):
    """Модель связи жанров и произведений."""

    title = models.ForeignKey(
        Title, on_delete=models.CASCADE,
        verbose_name='Произведение'
    )
    genre = models.ForeignKey(
        Genre, on_delete=models.SET_NULL,
        verbose_name='Жанр',
        null=True
    )


class Review(models.Model):
    """Модель отзывов."""

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение',
    )
    text = models.CharField(max_length=const.REVIEW_TEXT_MAX_LENGTH)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    score = models.PositiveSmallIntegerField(
        'Рейтинг',
        validators=(
            MinValueValidator(
                const.MINIMUM_RATING,
                f'Рейтинг не может быть ниже {const.MINIMUM_RATING}'
            ),
            MaxValueValidator(
                const.MAXIMUM_RATING,
                f'Рейтинг не может быть выше {const.MAXIMUM_RATING}'
            )
        )
    )
    pub_date = models.DateField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        default_related_name = '%(class)ss'
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author',),
                name='unique review',
            )
        ]
        ordering = ('pub_date',)

    def __str__(self):
        return self.text[:const.MAX_STR_LENGTH]


class Comment(models.Model):
    """Модель комментариев."""

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Отзыв',
    )
    text = models.CharField(
        'Текст комментария', max_length=const.MAX_LENGTH_FIELD
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True, db_index=True
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = '%(class)ss'

    def __str__(self):
        return self.text[:const.MAX_STR_LENGTH]
