import structlog
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, viewsets, mixins
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apis.serializers.version import VersionRequestSerializer, VersionResponseSerializer
from apis.serializers.page import PageResponseSerializer
from docs.models import Version, Page
from utils.decorators import IsStaffOrAdminUser

logger = structlog.getLogger('wz-doc')


class VersionViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    serializer_class = VersionRequestSerializer
    queryset = Version.objects.all()

    def get_permissions(self):
        if self.action in ('create', 'update', 'destroy'):
            permission_classes = (IsStaffOrAdminUser,)
        else:
            permission_classes = (IsAuthenticated,)

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        if (self.request.user.is_superuser, self.request.user.is_staff) == (False, False):
            # if it is not a superadmin or not a staff we check
            #permissions_code = Permission.objects.filter(group__user=self.request.user).values_list('codename', flat=True)
            user_permissions = (
                    Permission.objects.filter(group__user=self.request.user) |
                    self.request.user.user_permissions.all()
            ).values_list('id', flat=True)

            logger.info('VERSION-QUERYSET', permissions_ids=user_permissions)

            return Version.objects.filter(permission_id__in=user_permissions).order_by('name')

        return Version.objects.all().order_by('name')

    @swagger_auto_schema(
        operation_description="Create a Documentation Version",
        request_body=VersionRequestSerializer,
        responses={status.HTTP_201_CREATED: VersionResponseSerializer()},
        tags=['docs-version']
    )
    def create(self, request, *args, **kwargs):
        try:
            logger.info('DOCS_VERSION_CREATE-DATA', data=request.data)
            serializer = self.serializer_class(data=request.data)
            if not serializer.is_valid():
                return Response({'message': serializer.errors, 'code': '400'}, status=status.HTTP_400_BAD_REQUEST)

            version = serializer.save()

            logger.info('DOCS_VERSION_CREATE-CREATE_PERMISSION', data=request.data)
            content_type = ContentType.objects.get_for_model(Version)
            permission = Permission.objects.create(
                codename=request.data['name'].lower(),
                name=request.data['name'].title(),
                content_type=content_type
            )
            version.permission = permission
            version.save()

            logger.info('DOCS_VERSION_CREATE-CREATE_GROUP', data=request.data)
            group = Group.objects.create(name=serializer.data['name'])
            group.permissions.add(permission)

            serializer = VersionResponseSerializer(instance=version)
            return Response({'data': serializer.data, 'code': '201'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'message': str(e), 'code': '500'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="List all Documentations Versions",
        responses={status.HTTP_200_OK: VersionResponseSerializer()},
        tags=['docs-version']
    )
    def list(self, request, *args, **kwargs):
        """
        List All Documentations version

        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        try:
            page = self.paginator.paginate_queryset(queryset=self.get_queryset(), request=request)
            serializer = VersionResponseSerializer(page, many=True)
            return self.paginator.get_paginated_response({'data':serializer.data, 'code': '200'})
        except Exception as e:
            return Response({'message': str(e), 'code': '500'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Update Version information",
        responses={status.HTTP_200_OK: VersionResponseSerializer()},
        tags=['docs-version']
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a Documentation version
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
        operation_description="Update Version information",
        responses={status.HTTP_201_CREATED: VersionResponseSerializer()},
        tags=['docs-version']
    )
    def update(self, request, *args, **kwargs):
        """
        Update Documentation Version
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        try:
            instance = self.get_object()
            instance_group = Group.objects.get(name=instance.name)

            logger.info('DOCS_VERSION_UPDATE-DATA', data=request.data)
            serializer = self.serializer_class(
                instance=instance,
                data=request.data,
                partial=True
            )
            if not serializer.is_valid():
                return Response({'message': serializer.errors, 'code': '400'}, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            if 'name' in request.data:
                logger.info('DOCS_VERSION_UPDATE-UPDATE_GROUP_NAME', data=request.data)
                instance.permission.name = serializer.data['name'].title()
                instance.permission.codename = serializer.data['name'].lower()
                instance.permission.save()

                instance_group.name = serializer.data['name']
                instance_group.save()

            serializer = VersionResponseSerializer(instance=instance)
            return Response({'data': serializer.data, 'code': '201'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'message': str(e), 'code': '500'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(operation_description="Delete a documentation version", request_body=None, responses={202: openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'message': openapi.Schema(type=openapi.TYPE_STRING),
            'code': openapi.Schema(type=openapi.TYPE_STRING),
        }
    )}, tags=['docs-version'])
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            logger.info('DOCS_VERSION_DELETE', id=kwargs.get('pk'))

            instance_group = Group.objects.get(name=instance.name)

            instance.delete()
            logger.info('DOCS_VERSION_DELETE-DELETE_GROUP', id=kwargs.get('pk'))
            instance_group.delete()

            return Response({'message': 'Documentation Version deleted successfully', 'code': '202'}, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            return Response({'message': str(e), 'code': '500'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="List All pages related to a Documentation Version",
        responses={status.HTTP_200_OK: PageResponseSerializer()},
        tags=['docs-version'])
    @action(methods=['GET'], detail=True)
    def pages(self, request, pk):
        """
        List all Pages related to a specific versions

        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        try:
            version = self.get_object()
            logger.info('LIST_PAGES-DATA', version=version.name)
            version_pages = Page.objects.filter(version=version).order_by('name')

            if (self.request.user.is_superuser, self.request.user.is_staff) == (False, False) \
                    and self.request.user.groups.filter(name=version.name).exists() is False:
                logger.info('LIST_PAGES-NOT_STAFF')

                user_permissions = self.request.user.user_permissions.all().values_list('id', flat=True)
                version_pages = version_pages.filter(version=version, permission__id__in=user_permissions)

                if version_pages.count() == 0:
                    return Response(
                        {'message': 'User does not have right access to Pages of this Version', 'code': '400'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            page = self.paginator.paginate_queryset(queryset=version_pages, request=request)

            serializer = PageResponseSerializer(page, many=True)
            return self.paginator.get_paginated_response({'data': serializer.data, 'code': '200'})
        except Exception as e:
            return Response({'message': str(e), 'code': '500'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

