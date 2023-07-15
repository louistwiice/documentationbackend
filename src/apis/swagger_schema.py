from django.conf import settings

from rest_framework import permissions

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator



# Schema configuration
swagger_schema_view = get_schema_view(
    openapi.Info(title="Wizall Documentation", default_version="0.1.0"),
    validators=["flex", "ssv"],
    public=True,
    permission_classes=[permissions.IsAuthenticated],
    url= settings.SWAGGER_BASE_URL,
)
