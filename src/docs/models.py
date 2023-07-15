from django.db import models
from django.contrib.auth.models import Permission
# Create your models here.


class Version(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=500, null=True, blank=True)
    permission = models.OneToOneField(Permission, on_delete=models.CASCADE, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = self.name.title()

        super(Version, self).save(*args, **kwargs)


class Page(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    is_under_maintenance = models.BooleanField(default=False, help_text="Is the Page under maintenance. If Yes, A Custom message should be shown")
    version = models.ForeignKey(Version, on_delete=models.CASCADE)
    permission = models.OneToOneField(Permission, on_delete=models.CASCADE, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('name', 'version')

    def save(self, *args, **kwargs):
        self.name = self.name.title()

        super(Page, self).save(*args, **kwargs)

    # @property
    # def parts(self):
    #     return Part.objects.filter(page=self)


class Part(models.Model):
    name = models.CharField(max_length=200)
    content = models.TextField()
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    permission = models.OneToOneField(Permission, on_delete=models.CASCADE, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('name', 'page')

    def save(self, *args, **kwargs):
        self.name = self.name.title()

        super(Part, self).save(*args, **kwargs)
