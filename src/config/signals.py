from django.dispatch import receiver
from django_structlog.signals import bind_extra_request_metadata
import structlog


@receiver(bind_extra_request_metadata)
def bind_user_info(request, logger, **kwargs):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    if getattr(request, 'user', '') == '':
        structlog.contextvars.bind_contextvars(
            username='Anonymous',
            is_staff=None,
            ip=ip
        )

    else:
        structlog.contextvars.bind_contextvars(
            username=getattr(request.user, 'username', ''),
            is_staff=getattr(request.user, 'is_staff', ''),
            ip=ip
        )

