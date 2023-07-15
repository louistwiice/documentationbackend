import structlog
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, viewsets, mixins
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apis.serializers.page import PageRequestSerializer, PageResponseSerializer, PageWithPartSerializer
from apis.serializers.part import PartResponseSerializer
from docs.models import Page, Version, Part
from utils.decorators import IsStaffOrAdminUser

logger = structlog.getLogger('wz-doc')


class PageViewSet(
    mixins.CreateModelMixin, mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    serializer_class = PageRequestSerializer
    queryset = Page.objects.none()

    def get_permissions(self):
        if self.action in ('create', 'update', 'destroy'):
            permission_classes = (IsStaffOrAdminUser,)
        else:
            permission_classes = (IsAuthenticated,)

        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PageWithPartSerializer
        else:
            return PageRequestSerializer

    def get_queryset(self):
        if (self.request.user.is_superuser, self.request.user.is_staff) == (False, False):
            # if it is not a superadmin or not a staff we check
            #permissions_code = Permission.objects.filter(group__user=self.request.user).values_list('codename', flat=True)
            user_permissions = (
                Permission.objects.filter(group__user=self.request.user) |
                self.request.user.user_permissions.all()
            ).values_list('id', flat=True)

            logger.info('PAGE-QUERYSET', permissions_ids=user_permissions)

            return Page.objects.filter(permission__id__in=user_permissions).order_by('name')

        return Page.objects.all().order_by('name')

    @swagger_auto_schema(operation_description="Create a Page", request_body=PageRequestSerializer, responses={status.HTTP_201_CREATED: PageResponseSerializer()}, tags=['docs-page'])
    def create(self, request, *args, **kwargs):
        try:
            logger.info('PAGE_CREATE-DATA', data=request.data)
            serializer_class = self.get_serializer_class()
            serializer = serializer_class(data=request.data)
            if not serializer.is_valid():
                return Response({'message': serializer.errors, 'code': '400'}, status=status.HTTP_400_BAD_REQUEST)

            version = Version.objects.get(id=request.data['version'])
            permission_code = f"{version.name.lower()}" \
                              f"-{request.data['name'].lower().replace(' ', '_')}"

            page = serializer.save()
            logger.info('PAGE_CREATE-CREATE_PERMISSION', data=request.data)

            content_type = ContentType.objects.get_for_model(Page)
            permission = Permission.objects.create(
                codename=permission_code,
                name=f"{version.name} - {serializer.data['name']}",
                content_type=content_type
            )
            page.permission = permission
            page.save()

            logger.info('PAGE_CREATE-ASSOCIATE_PERMISSION_TO_GROUP', data=request.data)
            group = Group.objects.get(name=version.name)
            group.permissions.add(permission)

            serializer = PageResponseSerializer(instance=page)

            return Response({'data': serializer.data, 'code': '201'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'message': str(e), 'code': '500'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(operation_description="Retrieve a Page", responses={status.HTTP_200_OK: PageWithPartSerializer()}, tags=['docs-page'])
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a Documentation Page
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        try:
            instance = self.get_object()
            #serializer = self.serializer_class(instance=instance)
            serializer_class = self.get_serializer_class()
            serializer = serializer_class(instance=instance)
            return Response({'data': serializer.data, 'code': '200'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': str(e), 'code': '500'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(operation_description="Update a Documentation Page", responses={status.HTTP_201_CREATED: PageResponseSerializer()}, tags=['docs-page'])
    def update(self, request, *args, **kwargs):
        """
        Retrieve a Documentation Page
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        try:
            instance = self.get_object()
            old_version_name = instance.version.name.lower()
            switch_group = False

            logger.info('PAGE_UPDATE-DATA', data=request.data)
            serializer_class = self.get_serializer_class()

            serializer = serializer_class(
                instance=instance,
                data=request.data,
                partial=True
            )
            if not serializer.is_valid():
                return Response({'message': serializer.errors, 'code': '400'}, status=status.HTTP_400_BAD_REQUEST)

            if 'name' in request.data or 'version' in request.data:

                if 'version' in request.data:
                    version = Version.objects.get(id=request.data['version'])
                    old_version = instance.version

                    if old_version != version:
                        switch_group = True

                else:
                    version = instance.version

                permission_code = f"{version.name.lower()}" \
                                  f"-{request.data.get('name', instance.name).lower().replace(' ', '_')}"

                serializer.save()

                logger.info('PAGE_UPDATE-UPDATE_PERMISSION', data=request.data, permission_code=permission_code)
                instance.permission.codename = permission_code
                instance.permission.name = f"{version.name} - {serializer.data['name']}"
                instance.permission.save()

                if switch_group:
                    logger.info(
                        'PAGE_UPDATE-UPDATE_GROUP',
                        data=request.data, old_version_name=old_version_name, permission_code=permission_code
                    )

                    old_group = Group.objects.get(name=old_version_name.title())
                    old_group.permissions.remove(instance.permission)

                    new_group = Group.objects.get(name=instance.version.name)
                    new_group.permissions.add(instance.permission)

            else:
                serializer.save()

            serializer = PageResponseSerializer(instance=instance)
            return Response({'data': serializer.data, 'code': '200'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': str(e), 'code': '500'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(operation_description="Delete a documentation Page", request_body=None, responses={202: openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'message': openapi.Schema(type=openapi.TYPE_STRING),
            'code': openapi.Schema(type=openapi.TYPE_STRING),
        }
    )}, tags=['docs-page'])
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            logger.info('PAGE_DELETE-DATA', id=kwargs.get('pk'), name=instance.name)

            logger.info('PAGE_DELETE-DELETE_PERMISSION', id=kwargs.get('pk'))
            instance.permission.delete()

            logger.info('PAGE_DELETE-INSTANCE', id=kwargs.get('pk'))
            instance.delete()

            return Response({'message': 'Documentation Page deleted successfully', 'code': '202'}, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            return Response({'message': str(e), 'code': '500'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="List All Parts related to a Documentation Page",
        responses={status.HTTP_200_OK: PartResponseSerializer()},
        tags=['docs-page'])
    @action(methods=['GET'], detail=True)
    def parts(self, request, pk):
        try:
            instance = self.get_object()
            logger.info('LIST_PART-DATA', page=instance.name)
            page_parts = Part.objects.filter(page=instance).order_by('name')

            if (self.request.user.is_superuser, self.request.user.is_staff) == (False, False) \
                    and self.request.user.groups.filter(name=instance.version.name).exists() is False:
                logger.info('LIST_PART-NOT_STAFF')

                user_permissions = self.request.user.user_permissions.all().values_list('id', flat=True)

                logger.info('LIST_PART-NOT_STAFF_2', user_permissions=user_permissions)

                page_parts = page_parts.filter(permission__id__in=user_permissions)
                if page_parts.count() == 0:
                    return Response(
                        {'message': 'User does not have right access to Contents of this Pages', 'code': '400'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            page = self.paginator.paginate_queryset(queryset=page_parts, request=request)

            serializer = PartResponseSerializer(page, many=True)
            return self.paginator.get_paginated_response({'data': serializer.data, 'code': '200'})
        except Exception as e:
            return Response({'message': str(e), 'code': '500'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
