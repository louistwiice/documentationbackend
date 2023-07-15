from django.contrib import admin
from docs.models import Version, Page, Part
# Register your models here.


@admin.register(Version)
class VersionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description']


class PartInLine(admin.TabularInline):
    model = Part


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    search_fields = [field.name for field in Page._meta.get_fields()]
    list_display = ['id', 'version', 'name', 'is_under_maintenance']
    inlines = [PartInLine]
