import structlog
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, viewsets, mixins
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apis.serializers.part import PartRequestSerializer, PartResponseSerializer
from docs.models import Part, Page
from utils.decorators import IsStaffOrAdminUser

logger = structlog.getLogger('wz-doc')


class PartViewSet(
    mixins.CreateModelMixin, mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    serializer_class = PartRequestSerializer
    queryset = Part.objects.none()

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

            logger.info('PART-QUERYSET', permissions_ids=user_permissions)

            return Part.objects.filter(permission__id__in=user_permissions)

        return Part.objects.all()

    @swagger_auto_schema(
        operation_description="Create a Part of a Page",
        request_body=PartRequestSerializer, responses={status.HTTP_201_CREATED: PartResponseSerializer()},
        tags=['docs-page-part']
    )
    def create(self, request, *args, **kwargs):
        try:
            logger.info('PAGE_PART_CREATE-DATA', data=request.data)
            serializer = self.serializer_class(data=request.data)
            if not serializer.is_valid():
                return Response({'message': serializer.errors, 'code': '400'}, status=status.HTTP_400_BAD_REQUEST)

            page = Page.objects.get(id=request.data['page'])
            permission_code = f"{page.version.name.lower()}" \
                              f"-{page.name.lower().replace(' ', '_')}" \
                              f"-{request.data['name'].lower().replace(' ', '_')}"

            part = serializer.save()
            logger.info('PAGE_PART_CREATE-CREATE_PERMISSION', data=request.data, permission_code=permission_code)

            content_type = ContentType.objects.get_for_model(Part)
            permission = Permission.objects.create(
                codename=permission_code,
                name=f"{page.version.name} - {page.name} - {serializer.data['name']}",
                content_type=content_type
            )
            part.permission = permission
            part.save()

            logger.info('PAGE_PART_CREATE-ASSOCIATE_PERMISSION_TO_GROUP', data=request.data)
            group = Group.objects.get(name=page.version.name)
            group.permissions.add(permission)

            serializer = PartResponseSerializer(instance=part)
            return Response({'data': serializer.data, 'code': '201'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'message': str(e), 'code': '500'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Retrieve a Part of a Page",
        responses={status.HTTP_200_OK: PartResponseSerializer()},
        tags=['docs-page-part']
    )
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
            serializer = PartResponseSerializer(instance=instance)
            return Response({'data': serializer.data, 'code': '200'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': str(e), 'code': '500'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(operation_description="Update a Documentation Page", responses={status.HTTP_201_CREATED: PartResponseSerializer()}, tags=['docs-page-part'])
    def update(self, request, *args, **kwargs):
        """
        Retrieve a Documentation Page
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        try:
            switch_group = False  # To check if we should switch the group where this part is associated

            instance = self.get_object()
            old_page_name = instance.page.name.lower()
            old_page_version = instance.page.version.name.lower()

            logger.info('PAGE_PART_UPDATE-DATA', data=request.data, old_page_version=old_page_version)
            serializer_class = self.get_serializer_class()

            serializer = serializer_class(
                instance=instance,
                data=request.data,
                partial=True
            )
            if not serializer.is_valid():
                return Response({'message': serializer.errors, 'code': '400'}, status=status.HTTP_400_BAD_REQUEST)

            if 'name' in request.data or 'page' in request.data:

                if 'page' in request.data:
                    page = Page.objects.get(id=request.data['page'])
                    old_page = instance.page

                    if old_page.version != page.version:
                        switch_group = True
                else:
                    page = instance.page

                permission_code = f"{page.version.name.lower()}" \
                                  f"-{page.name.lower().replace(' ', '_')}" \
                                  f"-{request.data.get('name', instance.name).lower().replace(' ', '_')}"

                serializer.save()

                logger.info('PAGE_PART_UPDATE-UPDATE_PERMISSION', data=request.data, permission_code=permission_code)
                instance.permission.codename = permission_code
                instance.permission.name = f"{page.version.name} - {instance.page.name} - {serializer.data['name']}"
                instance.permission.save()

                logger.info(
                    'PAGE_PART_UPDATE-UPDATE_GROUP',
                    data=request.data, old_page_name=old_page_name, permission_code=permission_code, switch_group=switch_group
                )

                if switch_group:
                    old_group = Group.objects.get(name=old_page.version.name)
                    old_group.permissions.remove(instance.permission)

                    new_group = Group.objects.get(name=page.version.name)
                    new_group.permissions.add(instance.permission)

            else:
                serializer.save()

            serializer = PartResponseSerializer(instance=instance)

            return Response({'data': serializer.data, 'code': '200'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': str(e), 'code': '500'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(operation_description="Delete a Part's Page", request_body=None, responses={202: openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'message': openapi.Schema(type=openapi.TYPE_STRING),
            'code': openapi.Schema(type=openapi.TYPE_STRING),
        }
    )}, tags=['docs-page-part'])
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            logger.info('PAGE_PART_DELETE-DATA', id=kwargs.get('pk'), name=instance.name)

            logger.info('PAGE_PART_DELETE-DELETE_PERMISSION', id=kwargs.get('pk'))
            instance.permission.delete()

            logger.info('PAGE_PART_DELETE', id=kwargs.get('pk'))
            instance.delete()

            return Response({'message': 'Part Page deleted successfully', 'code': '202'}, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            return Response({'message': str(e), 'code': '500'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
