import structlog
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from rest_framework import status, viewsets, mixins
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apis.serializers.users import UserInfoSerializer, UserFullSerializer, UpdatePasswordStaffSerializer, \
    UpdatePasswordSerializer, UserCreateSerializer
from users.models import User
from utils.decorators import IsStaffOrAdminUser

logger = structlog.getLogger('wz-doc')


class UserViewSet(
        mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
        mixins.DestroyModelMixin, viewsets.GenericViewSet):
    serializer_class = UserInfoSerializer
    permission_classes = (IsStaffOrAdminUser,)
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        else:
            return UserInfoSerializer

    @swagger_auto_schema(operation_description="Create a User", request_body=UserCreateSerializer, responses={status.HTTP_201_CREATED: UserInfoSerializer()})
    def create(self, request, *args, **kwargs):
        """
        Create a User

        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        try:
            logger.info('USERS_CREATE-DATA', data=request.data)
            serializer = UserCreateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({'message': serializer.errors, 'code': '400'}, status=status.HTTP_400_BAD_REQUEST)

            user = serializer.save()
            user.set_password(request.data['password'])
            user.save()

            serializer = UserCreateSerializer(instance=user)
            return Response({'data': serializer.data, 'code': '201'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'message': str(e), 'code': '500'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(operation_description="List all Users", responses={status.HTTP_200_OK: UserInfoSerializer()})
    def list(self, request, *args, **kwargs):
        """
        List All users

        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        try:
            page = self.paginator.paginate_queryset(
                queryset=self.get_queryset(), request=request)
            serializer = UserInfoSerializer(page, many=True)
            return self.paginator.get_paginated_response({'data': serializer.data, 'code': '200'})
        except Exception as e:
            return Response({'message': str(e), 'code': '500'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(operation_description="Retrieve User information", responses={status.HTTP_200_OK: UserFullSerializer()})
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a User
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        try:
            instance = self.get_object()
            serializer = self.serializer_class(instance=instance)
            return Response({'data': serializer.data, 'code': '200'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': str(e), 'code': '500'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Update User information",
        responses={status.HTTP_200_OK: UserFullSerializer()}
    )
    def update(self, request, *args, **kwargs):
        """
        Update a User
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        try:
            instance = self.get_object()
            logger.info('USERS-UPDATE', data=request.data)
            serializer = self.serializer_class(
                instance=instance,
                data=request.data,  # or request.data
                partial=True
            )
            if not serializer.is_valid():
                return Response({'message': serializer.errors, 'code': '400'}, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()

            serializer = UserFullSerializer(instance=instance)
            return Response({'data': serializer.data, 'code': '201'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'message': str(e), 'code': '500'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(operation_description="Delete a User", request_body=None, responses={202: openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'message': openapi.Schema(type=openapi.TYPE_STRING),
            'code': openapi.Schema(type=openapi.TYPE_STRING),
        }
    )})
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.delete()

            return Response({'message': 'User deleted successfully', 'code': '202'}, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            return Response({'message': str(e), 'code': '500'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(operation_description="Update User Password", request_body=UpdatePasswordSerializer, responses={200: openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'message': openapi.Schema(type=openapi.TYPE_STRING),
            'code': openapi.Schema(type=openapi.TYPE_STRING),
        }
    )})
    @action(detail=True, methods=["POST"], permission_classes=[IsAuthenticated])
    def change_password(self, request, pk):
        try:
            instance = self.get_object()
            logger.info('UPDATE_PASSWORD-DATA', data=request.data,
                        connected_id=str(request.user.id), updated_to_user=pk)
            serializer = UpdatePasswordSerializer(
                data=request.data, instance=instance)

            if (request.user.is_staff, request.user.is_superuser) == (False, False):
                logger.info('UPDATE_PASSWORD-NOT_MEMBER_USER')

                if request.user != instance:
                    return Response({'message': 'Can not perform action on another user', 'code': '400'}, status=status.HTTP_400_BAD_REQUEST)

                if not serializer.is_valid():
                    return Response({'message': serializer.errors, 'code': '400'}, status=status.HTTP_400_BAD_REQUEST)

            serializer.update(instance, request.data)

            return Response({'message': 'Password successfully updated', 'code': '200'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': str(e), 'code': '500'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(operation_description="Information about connected user", request_body=None, responses={200: UserFullSerializer()})
    @action(detail=False, methods=["GET"], permission_classes=[IsAuthenticated])
    def connected_user(self, request):
        try:
            logger.info('ME-DATA', username=request.user.username)

            serializer = UserFullSerializer(instance=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': str(e), 'code': '500'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
