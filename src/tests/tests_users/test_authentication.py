import json

import pytest
from config.conf import ACCESS_TOKEN_LIFETIME_MINUTES, REFRESH_TOKEN_LIFETIME_DAYS


class TestExample:

    def test_example(self, example_value):
        """
        example_value is a function located in conftest.py.

        :param example_value:
        :return:
        """
        assert example_value == 39


@pytest.mark.user_auth
class TestLogin:
    url = '/api/auth/login/'

    @pytest.mark.django_db
    def test_with_good_username_and_password_should_pass(self, client_api, admin_user_mike):
        response = client_api.post(self.url, {'identifier': admin_user_mike.username, 'password': 'mike'}, format='json')

        assert response.status_code == 200

        response_json = json.loads(response.content)
        assert 'access' in str(response.data)
        assert 'refresh' in str(response.data)
        assert 'access_expired_in' in str(response.data)
        assert 'refresh_expired_in' in str(response.data)
        assert response_json['access_expired_in'] == 60*ACCESS_TOKEN_LIFETIME_MINUTES
        assert response_json['refresh_expired_in'] == REFRESH_TOKEN_LIFETIME_DAYS

    @pytest.mark.django_db
    def test_with_good_email_and_password_should_pass(self, client_api, admin_user_mike):
        response = client_api.post(self.url, {'identifier': admin_user_mike.email, 'password': 'mike'}, format='json')

        assert response.status_code == 200

        assert 'access' in str(response.data)
        assert 'refresh' in str(response.data)
        assert 'access_expired_in' in str(response.data)
        assert 'refresh_expired_in' in str(response.data)
        assert response.data['access_expired_in'] == 60*ACCESS_TOKEN_LIFETIME_MINUTES
        assert response.data['refresh_expired_in'] == REFRESH_TOKEN_LIFETIME_DAYS

    @pytest.mark.django_db
    def test_non_existent_user_should_not_pass(self, client_api, admin_user_mike):
        response = client_api.post(self.url, {'identifier': "testeur", 'password': '12234'}, format='json')

        assert response.status_code == 400
        assert response.data['message']['identifier'][0] == "User Identifier (Email/Username) not found"

    @pytest.mark.django_db
    def test_with_wrong_password_should_not_pass(self, client_api, admin_user_mike):
        response = client_api.post(self.url, {'identifier': admin_user_mike.email, 'password': '12234'}, format='json')

        assert response.status_code == 400
        assert "Unable to log in with provided credentials." in str(response.data['message'])

    @pytest.mark.django_db
    def test_inactivated_user_should_not_pass(self, client_api, inactivated_user):
        response = client_api.post(self.url, {'identifier': inactivated_user.email, 'password': 'inactive'}, format='json')

        assert response.status_code == 400
        assert response.data['message']['identifier'][0] == 'User account is disabled.'


@pytest.mark.user_auth
class TestLogout:
    url = '/api/auth/logout/'

    def test_not_connected_user_should_return_403(self, client_api):
        response = client_api.get(self.url)

        assert response.status_code == 403
        assert response.data['detail'] == 'Authentication credentials were not provided.'

    @pytest.mark.django_db
    def test_connected_but_already_logged_out_return_208(self, client_api, admin_user_mike):
        client_api.login(username=admin_user_mike.username, password='mike')
        response = client_api.get(self.url)

        assert response.status_code == 208
