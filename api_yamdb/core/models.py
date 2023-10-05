from django.db import models

from reviews import const


class BaseNameSlugModel(models.Model):
    name = models.CharField(
        max_length=const.MAX_LENGTH_FIELD,
        unique=True,
        verbose_name='Название',
    )
    slug = models.SlugField(
        max_length=const.MAX_SLUG_LENGTH,
        unique=True,
        verbose_name='Идентификатор',
    )

    class Meta:
        default_related_name = '%(class)ss'
        ordering = ('name',)
        abstract = True

    def __str__(self):
        return self.slug[:const.MAX_STR_LENGTH]
