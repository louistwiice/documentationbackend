from django.apps import AppConfig
from django.core.signals import setting_changed


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        from config.signals import bind_user_info
        setting_changed.connect(bind_user_info)
