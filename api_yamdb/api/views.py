from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, views, viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from api.filters import TitleFilter
from api.mixins import GenericCreateListDestroyMixin
from api.permissions import IsAdmin, IsAuthorOrModeratorOrAdmin
from api.serializers import (
    CategorySerializer, CommentSerializer,
    GenreSerializer, GetTokensForUserSerializer,
    ReviewSerializer, TitleGetSerializer,
    TitlePostSerializer, UserSerializer,
    UserSignupSerializer, UserUpdateSerializer
)
from reviews.models import Category, Genre, Review, Title, User

ALLOWED_METHODS = ('get', 'post', 'patch', 'delete')


class CategoryViewSet(GenericCreateListDestroyMixin):
    """ViewSet для работы с категориями."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(GenericCreateListDestroyMixin):
    """ViewSet для работы с жанрами."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с отзывами."""

    serializer_class = ReviewSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrModeratorOrAdmin,
    )
    http_method_names = ALLOWED_METHODS

    @property
    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title.reviews.select_related('author')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title)


class TitleViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с произведениями."""

    http_method_names = ALLOWED_METHODS
    filter_backends = (filters.OrderingFilter, DjangoFilterBackend)
    filterset_class = TitleFilter
    ordering_fields = ('name',)
    ordering = ('name',)

    def get_queryset(self):
        return (
            Title.objects.select_related('category')
            .prefetch_related('genre')
            .annotate(rating=Avg('reviews__score'))
        )

    def get_serializer_class(self):
        return (
            TitleGetSerializer
            if self.action in ('list', 'retrieve')
            else TitlePostSerializer
        )


class UserSignupView(views.APIView):
    """Регистрация нового пользователя."""

    serializer_class = UserSignupSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user, created = User.objects.get_or_create(
                email=serializer.validated_data.get('email'),
                username=serializer.validated_data.get('username'),
            )
        except IntegrityError:
            return Response('Пользователь с таким именем или адресом '
                            'электронной почты уже существует.',
                            status=status.HTTP_400_BAD_REQUEST)
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            subject='Confirmation Code',
            message=(
                'Send a request with a confirmation code to receive a '
                f'token\n {confirmation_code}'
            ),
            from_email=None,
            recipient_list=(user.email,)
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetTokensForUserView(views.APIView):
    """Получение JWT-токена."""

    serializer_class = GetTokensForUserSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        confirmation_code = serializer.validated_data.get('confirmation_code')
        user = get_object_or_404(User, username=username)
        if not default_token_generator.check_token(user, confirmation_code):
            return Response(
                f'Invalid code for {user} - {confirmation_code}',
                status=status.HTTP_400_BAD_REQUEST,
            )
        token = RefreshToken.for_user(user)
        return Response(
            {'access': str(token.access_token)}, status=status.HTTP_200_OK
        )


class UserViewSet(viewsets.ModelViewSet):
    """Работа со списком пользователей."""

    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated, IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'
    queryset = User.objects.all()
    http_method_names = ALLOWED_METHODS


class UserUpdateView(views.APIView):
    """Получение и изменение данных своей учетной записи."""

    serializer_class = UserUpdateSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        return Response(self.serializer_class(request.user).data)

    def patch(self, request, format=None):
        serializer = self.serializer_class(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с комментариями."""

    serializer_class = CommentSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrModeratorOrAdmin,
    )
    http_method_names = ALLOWED_METHODS

    @property
    def get_review(self):
        return get_object_or_404(Review, pk=self.kwargs.get('review_id'))

    def get_queryset(self):
        return self.get_review.comments.select_related('author')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review)
