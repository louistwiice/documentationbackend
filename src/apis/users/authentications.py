import structlog
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework import status, viewsets
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from apis.serializers.authentications import AuthenticationRequestSerializer, AuthenticationResponseSerializer, TokenRefreshResponseSerializer
from config.conf import AUTH_HEADER_TYPES, ACCESS_TOKEN_LIFETIME_MINUTES, REFRESH_TOKEN_LIFETIME_DAYS

logger = structlog.getLogger('wz-doc')


class CustomAuthUserViewSet(viewsets.GenericViewSet):
    serializer_class = AuthenticationRequestSerializer
    #renderer_classes = (CustomJSONRenderer, )

    @swagger_auto_schema(operation_description="User Login", responses={status.HTTP_200_OK: AuthenticationResponseSerializer()})
    @action(detail=False, methods=['POST'], permission_classes=[AllowAny], url_name='login')
    def login(self, request):
        try:
            logger.info('LOGIN-DATA', data=request.data)

            serializer = self.serializer_class(
                data=request.data,
                context={"request": request}
            )
            if not serializer.is_valid():
                return Response({"message": serializer.errors, "code": "400"}, status=status.HTTP_400_BAD_REQUEST)

            user = serializer.validated_data["user"]
            logger.info('LOGIN-SUCCESS', data=request.data)

            refresh = RefreshToken.for_user(user)
            request.session['username'] = user.username
            response = AuthenticationResponseSerializer(
                instance={
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'user': user,
                    'token_type': AUTH_HEADER_TYPES,
                    'access_expired_in': 60*ACCESS_TOKEN_LIFETIME_MINUTES,
                    'refresh_expired_in': REFRESH_TOKEN_LIFETIME_DAYS
                }
            )

            return Response(response.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"message": str(e), "code": "500"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(operation_description="Disconnect an User", responses={status.HTTP_200_OK: openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'message': openapi.Schema(type=openapi.TYPE_STRING, title='Response Message'),
            'code': openapi.Schema(type=openapi.TYPE_STRING, title='code')
        }
    )})
    @action(detail=False, methods=['GET'], url_name='logout')
    def logout(self, request):
        try:
            del request.session['username']
            response = {
                "message": "User successfully disconnected",
                "code": "200"
            }
        except:
            response = {
                "message": "User already disconnected",
                "code": "208"
            }

        return Response(response, status=int(response['code']))


class CustomTokenRefreshView(TokenRefreshView):
    @swagger_auto_schema(
        operation_description="Return a new access and refresh Token to the connected User",
        responses={status.HTTP_200_OK: TokenRefreshResponseSerializer()},
        tags=['auth']
    )
    def post(self, request, *args, **kwargs):
        user_session = request.session.get(request.user.username)
        if user_session is None:
            return Response({'message': 'User Disconnected. Please Login', 'code': '401'}, status=status.HTTP_401_UNAUTHORIZED)

        return super().post(request, *args, **kwargs)


class CustomTokenVerifyView(TokenVerifyView):
    @swagger_auto_schema(
        operation_description="Verify User access Token",
        responses={status.HTTP_200_OK: TokenRefreshResponseSerializer()},
        tags=['auth']
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
