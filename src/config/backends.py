from django.contrib.auth.backends import ModelBackend, UserModel
from django.db.models import Q
from rest_framework.renderers import JSONRenderer


class CustomBackendAuthentication(ModelBackend):
    """
    Custom method called during User authentication in api. User needs to authenticate by email or (phone, country).
    That's whey we implement the class and add it in AUTHENTICATION_BACKENDS variables in settings.py
    """
    def authenticate(self, request, identifier=None, password=None, **kwargs):
        try:
            user = UserModel.objects.get(Q(username=identifier) | Q(email=identifier))

        except UserModel.DoesNotExist:
            UserModel().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user

    def get_user(self, user_id):
        try:
            user = UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None

        return user if self.user_can_authenticate(user) else None


class CustomJSONRenderer(JSONRenderer):

    def render(self, data, accepted_media_type=None, renderer_context=None, **kwargs):
        response = {'data': data} if 'data' not in data else {'data': data['data']}
        if 'code' in data:
            response['code'] = data['code']
            data.pop('code')
        else:
            response['code'] = f"0{renderer_context.get('response').status_code}"

        if 'message' in data:
            response['message'] = data['message']
            data.pop('message')
        else:
            response['message'] = None

        return super(CustomJSONRenderer, self).render(response, accepted_media_type, renderer_context)
