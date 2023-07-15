import structlog
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, viewsets, mixins
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth.models import Group

from docs.models import Version, Page, Part
from apis.serializers.users import UserFullSerializer, PermissionGrantRequest, PermissionDenyRequest, GroupGrantRequest, \
    GroupDenyRequest, GroupSerializer
from utils.decorators import IsStaffOrAdminUser

logger = structlog.getLogger('wz-doc')


class UserDocsAccessViewSet(viewsets.GenericViewSet):
    """
    This View will help to manage User access to Version
    """
    permission_classes = (IsStaffOrAdminUser,)

    # =============================
    # ==== List Permissions or Groups available
    @swagger_auto_schema(
        operation_description="List all Group Documentation available",
        request_body=None,
        responses={
            status.HTTP_200_OK: GroupSerializer(),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'code': openapi.Schema(type=openapi.TYPE_STRING),
                }
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'code': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        },
        tags=['access management'])
    @action(methods=['GET'], detail=False)
    def groups(self, request):
        """
        List all Documentation groups available
        :param request:
        :return:
        """
        try:
            logger.info('LIST_GROUPS-START')
            names = Version.objects.all().values_list('name', flat=True)

            logger.info('LIST_GROUPS-NAMES', names=names)
            groups = Group.objects.filter(name__in=names).order_by('name')

            page = self.paginator.paginate_queryset(
                queryset=groups, request=request)

            serializer = GroupSerializer(page, many=True)
            return self.paginator.get_paginated_response({'data': serializer.data, 'code': '200'})
        except Exception as e:
            return Response({'message': str(e), 'code': '500'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="List all Permissions available",
        request_body=None,
        responses={
            status.HTTP_200_OK: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'data': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'versions': openapi.Schema(
                                description='Permission Created for each Version',
                                type=openapi.TYPE_ARRAY,
                                items=openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        'permission_id': openapi.Schema(type=openapi.TYPE_STRING, description="Permisison ID"),
                                        'permission__codename': openapi.Schema(type=openapi.TYPE_STRING, description="Permission Codename"),
                                    }
                                )
                            ),
                            'pages': openapi.Schema(
                                description='Permission Created for Each Page',
                                type=openapi.TYPE_ARRAY,
                                items=openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        'permission_id': openapi.Schema(type=openapi.TYPE_STRING,
                                                                        description="Permisison ID"),
                                        'permission__codename': openapi.Schema(type=openapi.TYPE_STRING,
                                                                               description="Permission Codename"),
                                    }
                                )
                            ),
                            'parts': openapi.Schema(
                                description='Permission Created for each Part of pages',
                                type=openapi.TYPE_ARRAY,
                                items=openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        'permission_id': openapi.Schema(type=openapi.TYPE_STRING,
                                                                        description="Permisison ID"),
                                        'permission__codename': openapi.Schema(type=openapi.TYPE_STRING,
                                                                               description="Permission Codename"),
                                    }
                                )
                            ),
                        }
                    ),
                    'code': openapi.Schema(type=openapi.TYPE_STRING),
                }
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'code': openapi.Schema(type=openapi.TYPE_STRING),
                }
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'code': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        },
        tags=['access management'])
    @action(methods=['GET'], detail=False)
    def permissions(self, request):
        """
        List all permissions created (Permissions on Versions, Pages and Parts)
        :param request:
        :return:
        """
        try:
            logger.info('LIST_PERMISSIONS-START')
            data = {
                'versions': Version.objects.all().order_by('permission__codename').values('permission_id', 'permission__codename'),
                'pages': Page.objects.all().order_by('permission__codename').values('permission_id', 'permission__codename'),
                'parts': Part.objects.all().order_by('permission__codename').values('permission_id', 'permission__codename'),
            }

            logger.info('LIST_PERMISSIONS-DATA', data=data)

            return Response({'data': data, 'code': '200'})
        except Exception as e:
            return Response({'message': str(e), 'code': '500'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # =========================================
    # ==== Grant or Remove permission to a User
    @swagger_auto_schema(
        operation_description="Give a User Access Permission to a Documentation (Version, Page or Part)",
        request_body=PermissionGrantRequest,
        responses={
            status.HTTP_202_ACCEPTED: UserFullSerializer(),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'code': openapi.Schema(type=openapi.TYPE_STRING),
                }
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'code': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        },
        tags=['access management'])
    @action(methods=['POST'], detail=False)
    def grant_user_permission(self, request):
        """
        Give a Permission to a User
        :param request:
        :return:
        """
        try:
            logger.info('GRANT_VERSION_PERMISSIONS-DATA', data=request.data)

            serializer = PermissionGrantRequest(data=request.data)
            if serializer.is_valid() is False:
                return Response({'message': serializer.errors, 'code': '400'}, status=status.HTTP_400_BAD_REQUEST)

            user = serializer.save()
            serializer = UserFullSerializer(instance=user)
            return Response({'data': serializer.data, 'code': '202'}, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            return Response({'message': str(e), 'code': '500'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Remove a User Access Permission to a Documentation (Version, Page or Part)",
        request_body=PermissionDenyRequest,
        responses={
            status.HTTP_202_ACCEPTED: UserFullSerializer(),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'code': openapi.Schema(type=openapi.TYPE_STRING),
                }
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'code': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        },
        tags=['access management'])
    @action(methods=['POST'], detail=False)
    def deny_user_permission(self, request):
        """
        Remove a permission to a User
        :param request:
        :return:
        """
        try:
            logger.info('DENY_VERSION_PERMISSIONS-DATA', data=request.data)

            serializer = PermissionDenyRequest(data=request.data)
            if serializer.is_valid() is False:
                return Response({'message': serializer.errors, 'code': '400'}, status=status.HTTP_400_BAD_REQUEST)

            user = serializer.save()
            serializer = UserFullSerializer(instance=user)
            return Response({'data': serializer.data, 'code': '202'}, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            return Response({'message': str(e), 'code': '500'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Give a User Access to all Documentation Groups.",
        request_body=GroupGrantRequest,
        responses={
            status.HTTP_202_ACCEPTED: UserFullSerializer(),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'code': openapi.Schema(type=openapi.TYPE_STRING),
                }
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'code': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        },
        tags=['access management'])
    @action(methods=['POST'], detail=False)
    def grant_user_group(self, request):
        """
        Put a User in a Documentation Group
        :param request:
        :return:
        """
        try:
            logger.info('GRANT_VERSION_PERMISSIONS-DATA', data=request.data)

            serializer = GroupGrantRequest(data=request.data)
            if serializer.is_valid() is False:
                return Response({'message': serializer.errors, 'code': '400'}, status=status.HTTP_400_BAD_REQUEST)

            user = serializer.save()
            serializer = UserFullSerializer(instance=user)
            return Response({'data': serializer.data, 'code': '202'}, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            return Response({'message': str(e), 'code': '500'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # @swagger_auto_schema(
    #     operation_description="Give a User Access to all specific Documentation Version Include Version, Page and Part.",
    #     request_body=GroupGrantRequest,
    #     responses={
    #         status.HTTP_202_ACCEPTED: UserFullSerializer(),
    #         status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Schema(
    #             type=openapi.TYPE_OBJECT,
    #             properties={
    #                 'message': openapi.Schema(type=openapi.TYPE_STRING),
    #                 'code': openapi.Schema(type=openapi.TYPE_STRING),
    #             }
    #         ),
    #         status.HTTP_400_BAD_REQUEST: openapi.Schema(
    #             type=openapi.TYPE_OBJECT,
    #             properties={
    #                 'message': openapi.Schema(type=openapi.TYPE_STRING),
    #                 'code': openapi.Schema(type=openapi.TYPE_STRING),
    #             }
    #         )
    #     },
    #     tags=['access management'])
    # @action(methods=['POST'], detail=False)
    # def grant_user_group(self, request):
    #     """
    #     Remove User from a Documentation Group
    #     :param request:
    #     :return:
    #     """
    #     try:
    #         logger.info('GRANT_VERSION_PERMISSIONS-DATA', data=request.data)
    #
    #         serializer = GroupGrantRequest(data=request.data)
    #         if serializer.is_valid() is False:
    #             return Response({'message': serializer.errors, 'code': '400'}, status=status.HTTP_400_BAD_REQUEST)
    #
    #         user = serializer.save()
    #         serializer = UserFullSerializer(instance=user)
    #         return Response({'data': serializer.data, 'code': '202'}, status=status.HTTP_202_ACCEPTED)
    #     except Exception as e:
    #         return Response({'message': str(e), 'code': '500'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Remove a User Access to all specific  Documentation Groups.",
        request_body=GroupDenyRequest,
        responses={
            status.HTTP_202_ACCEPTED: UserFullSerializer(),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'code': openapi.Schema(type=openapi.TYPE_STRING),
                }
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'code': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        },
        tags=['access management'])
    @action(methods=['POST'], detail=False)
    def deny_user_group(self, request):
        try:
            logger.info('GRANT_VERSION_PERMISSIONS-DATA', data=request.data)

            serializer = GroupDenyRequest(data=request.data)
            if serializer.is_valid() is False:
                return Response({'message': serializer.errors, 'code': '400'}, status=status.HTTP_400_BAD_REQUEST)

            user = serializer.save()
            serializer = UserFullSerializer(instance=user)
            return Response({'data': serializer.data, 'code': '202'}, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            return Response({'message': str(e), 'code': '500'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
