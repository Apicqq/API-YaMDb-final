from rest_framework import filters
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin
)
from rest_framework.viewsets import GenericViewSet


class GenericCreateListDestroyMixin(
    CreateModelMixin, ListModelMixin, DestroyModelMixin, GenericViewSet
):
    """Базовый миксин для Create, List, Destroy операций."""

    search_fields = ('name',)
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    ordering_fields = ('name',)
    ordering = ('name',)
