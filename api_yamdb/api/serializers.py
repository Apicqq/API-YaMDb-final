from django.core.validators import MaxValueValidator, MinValueValidator
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api import const
from reviews.models import Category, Comment, Genre, Review, Title, User


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Category."""

    class Meta:
        model = Category
        fields = (
            'name',
            'slug',
        )


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Genre."""

    class Meta:
        model = Genre
        fields = (
            'name',
            'slug',
        )


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Review."""

    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    score = serializers.IntegerField(
        validators=(
            MinValueValidator(
                const.MINIMUM_RATING,
                f'Рейтинг не может быть ниже {const.MINIMUM_RATING}'
            ),
            MaxValueValidator(
                const.MAXIMUM_RATING,
                f'Рейтинг не может быть выше {const.MAXIMUM_RATING}'
            ),
        )
    )

    def validate(self, data):
        request = self.context['request']
        if request.method != 'POST':
            return data
        title_id = self.context.get('view').kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if Review.objects.filter(title=title, author=request.user).exists():
            raise ValidationError('Должен быть только один отзыв.')
        return data

    class Meta:
        fields = '__all__'
        model = Review


class TitleSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для модели Title."""

    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = '__all__'


class TitleGetSerializer(TitleSerializer):
    """Сериализатор модели Title, предназначенный для безопасных методов."""

    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)


class TitlePostSerializer(TitleSerializer):
    """Сериализатор модели Title, предназначенный для методов POST и PATCH."""

    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all(), required=False
    )

    genre = serializers.SlugRelatedField(
        slug_field='slug', queryset=Genre.objects.all(), many=True
    )

    def validate_year(self, value):
        """Проверка года выпуска. Он не должен быть больше текущего."""
        if value > timezone.now().year:
            raise serializers.ValidationError(
                'Год выпуска не может быть больше текущего.'
            )
        return value

    def validate_genre(self, data):
        """Проверка поля жанра. Нельзя публиковать произведение без указания
        его жанра(ов)."""
        if not data:
            raise serializers.ValidationError(
                'Необходимо указать жанр(ы).'
            )
        return data

    def to_representation(self, instance):
        """Переопределяем метод to_representation, чтобы данные при
        POST-запросе выдавались как при GET-запросе."""
        return TitleGetSerializer(instance).data


class UserSerializer(serializers.ModelSerializer):
    """Сериализация данных для работы со списком пользователей."""

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                f'Использовать имя `{value}` в качестве `username` запрещено.'
            )
        return value


class UserUpdateSerializer(serializers.ModelSerializer):
    """Сериализация данных для управления своей учетной записью."""

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )
        read_only_fields = ('role',)


class UserSignupSerializer(serializers.Serializer):
    """Сериализация данных при регистрации пользователя."""

    username = serializers.RegexField(
        r'^[\w.@+-]+\Z',
        required=True,
        max_length=const.MAX_LENGTH_USERNAME_FIELD
    )
    email = serializers.EmailField(
        required=True, max_length=const.MAX_LENGTH_EMAIL_FIELD
    )

    def validate(self, data):
        if User.objects.filter(username=data.get('username')).exists():
            if User.objects.filter(email=data.get('email')).exists():
                return data
            raise ValidationError(
                'Пользователь с таким именем уже существует.'
            )
        if User.objects.filter(email=data.get('email')).exists():
            raise ValidationError(
                'Пользователь с таким адресом электронной почты уже '
                'существует.'
            )
        return data

    def validate_username(self, data):
        if data == 'me':
            raise ValidationError('Нельзя использовать "me" в '
                                  'качестве имени пользователя')
        return data


class GetTokensForUserSerializer(serializers.Serializer):
    """
    Сериализация данных при получении JWT-токена
    в обмен на `username` и `confirmation code`.
    """

    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)


class CommentSerializer(serializers.ModelSerializer):
    """Сериализация данных при получении комментариев к отзывам."""

    review = serializers.SlugRelatedField(slug_field='text', read_only=True)
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )

    class Meta:
        fields = '__all__'
        model = Comment
