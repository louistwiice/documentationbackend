from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from apis.users.authentications import (
    CustomAuthUserViewSet, CustomTokenRefreshView, CustomTokenVerifyView
)
from apis.users.authorizations import UserDocsAccessViewSet
from apis.users.space import UserViewSet
from apis.docs.version import VersionViewSet
from apis.docs.page import PageViewSet
from apis.docs.part import PartViewSet


router = DefaultRouter()

router.register(r'auth', CustomAuthUserViewSet, basename='custom_auth')
router.register(r'users', UserViewSet, basename='user_space')
router.register(r'docs/versions', VersionViewSet, basename='docs-versions')
router.register(r'docs/pages', PageViewSet, basename='docs-pages')
router.register(r'docs/parts', PartViewSet, basename='docs-parts')

router.register(r'docs/access', UserDocsAccessViewSet, basename='docs-access')


urlpatterns = [
    path("", include(router.urls)),

    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', CustomTokenVerifyView.as_view(), name='token_verify'),
]
