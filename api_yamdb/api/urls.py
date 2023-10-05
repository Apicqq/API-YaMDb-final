from api.views import (
    CategoryViewSet, CommentViewSet, GenreViewSet,
    GetTokensForUserView, ReviewViewSet, TitleViewSet,
    UserSignupView, UserUpdateView, UserViewSet
)
from django.urls import include, path
from rest_framework import routers

router = routers.DefaultRouter()

router.register('categories', CategoryViewSet, basename='categories')
router.register('genres', GenreViewSet, basename='genres')
router.register(
    r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='reviews'
)
router.register('titles', TitleViewSet, basename='titles')

router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments',
)

router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('v1/auth/token/', GetTokensForUserView.as_view(), name='token'),
    path('v1/auth/signup/', UserSignupView.as_view(), name='signup'),
    path('v1/users/me/', UserUpdateView.as_view(), name='me'),
    path('v1/', include(router.urls)),
]
