"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings
from config.conf import ENVIRONMENT
from django.conf.urls.static import static
from apis.swagger_schema import swagger_schema_view


schema_urls = [
    # Swagger
    re_path(
        r"swagger(?P<format>\.json|\.yaml)$",
        swagger_schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path(
        "swagger-docs",
        swagger_schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
]


app_urls = [
    path('admin/', admin.site.urls),
    path("api/", include("apis.urls")),
]

if ENVIRONMENT == 'production':
    # We should hide swagger in production
    urlpatterns = app_urls + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns = app_urls + schema_urls + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Django Admin site settings
admin.site.site_header = "Backend Documentation Admin"
admin.site.site_title = "Backend Documentation Admin"
admin.site.index_title = "Welcome to Wizall Backend Documentation Portal"

