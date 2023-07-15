import pytest
from apis.serializers.users import UserInfoSerializer


@pytest.mark.user_space
class TestCreate:
    url = '/api/users/'

    def test_unauthenticated_user_should_not_work(self, client_api):
        body = {}
        response = client_api.post(self.url, data=body, format='json')

        assert response.status_code == 403
        assert response.data['detail'] == 'Authentication credentials were not provided.'

    @pytest.mark.django_db
    def test_not_admin_or_not_staff_user_should_not_work(self, client_api, single_user_without_group):
        client_api.force_authenticate(user=single_user_without_group)
        body = {}
        response = client_api.post(self.url, data=body, format='json')

        assert response.status_code == 403
        assert response.data['detail'] == 'You do not have permission to perform this action.'

    @pytest.mark.django_db
    def test_create_with_no_username_should_not_work(self, client_api, admin_user):
        client_api.force_authenticate(user=admin_user)
        body = {'first_name': 'test'}
        response = client_api.post(self.url, data=body, format='json')

        assert response.status_code == 400
        assert 'This field is required.' in str(response.data['message'])
        assert 'username' in response.data['message']

    @pytest.mark.django_db
    def test_create_with_no_password_should_not_work(self, client_api, admin_user):
        client_api.force_authenticate(user=admin_user)
        body = {'first_name': 'test', 'username': 'test'}
        response = client_api.post(self.url, data=body, format='json')

        assert response.status_code == 400
        assert 'This field is required.' in str(response.data['message'])
        assert 'password' in response.data['message']

    @pytest.mark.django_db
    def test_create_with_existing_username_should_not_work(self, client_api, admin_user):
        client_api.force_authenticate(user=admin_user)
        body = {'first_name': 'test', 'username': admin_user.username,
                'password': admin_user.username}
        response = client_api.post(self.url, data=body, format='json')

        assert response.status_code == 400
        assert 'username' in response.data['message']
        assert 'user with this username already exists.' in str(
            response.data['message'])

    @pytest.mark.django_db
    def test_create_with_existing_email_should_not_work(self, client_api, admin_user):
        client_api.force_authenticate(user=admin_user)
        body = {'first_name': 'test', 'email': admin_user.email,
                'password': admin_user.username}
        response = client_api.post(self.url, data=body, format='json')

        assert response.status_code == 400
        assert 'email' in response.data['message']
        assert 'user with this email already exists.' in str(
            response.data['message'])

    @pytest.mark.django_db
    def test_create_only_username_should_work(self, client_api, admin_user):
        client_api.force_authenticate(user=admin_user)
        username = 'test'
        password = 'test'
        body = {'username': username, 'password': password}
        response = client_api.post(self.url, data=body, format='json')

        assert response.status_code == 201
        assert response.data['code'] == '201'
        assert response.data['data']['username'] == username
        assert response.data['data']['first_name'] == ''
        assert response.data['data']['is_active'] is True
        assert response.data['data']['is_staff'] is False

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "test_input",
        [
            {'username': 'test', 'first_name': 'test', 'last_name': 'test',
                'is_active': False, 'is_staff': False, 'password': 'test'},
            {'username': 'test', 'first_name': 'test', 'last_name': 'test',
                'is_active': True, 'is_staff': True, 'password': 'test'}
        ]
    )
    def test_create_with_good_params_should_work(self, client_api, admin_user, test_input):
        client_api.force_authenticate(user=admin_user)
        response = client_api.post(self.url, data=test_input, format='json')

        assert response.status_code == 201
        assert response.data['code'] == '201'
        assert response.data['data']['username'] == test_input['username']
        assert response.data['data']['first_name'] == test_input['first_name']
        assert response.data['data']['is_active'] == test_input['is_active']
        assert response.data['data']['is_staff'] == test_input['is_staff']


@pytest.mark.user_space
class TestList:
    url = '/api/users/'

    def test_unauthenticated_user_should_not_work(self, client_api):
        response = client_api.get(self.url)

        assert response.status_code == 403
        assert response.data['detail'] == 'Authentication credentials were not provided.'

    @pytest.mark.django_db
    def test_not_admin_or_not_staff_user_should_not_work(self, client_api, single_user_without_group):
        client_api.force_authenticate(user=single_user_without_group)
        response = client_api.get(self.url)

        assert response.status_code == 403
        assert response.data['detail'] == 'You do not have permission to perform this action.'

    @pytest.mark.django_db
    def test_connected_with_superadmin_should_work(self, client_api, admin_user, list_users_instances, mocker):
        client_api.force_authenticate(user=admin_user)
        mocker.patch('apis.users.space.UserInfoSerializer.data',
                     list_users_instances)
        response = client_api.get(self.url)

        assert response.status_code == 200
        assert 'count' in response.data
        assert 'next' in response.data
        assert 'previous' in response.data
        assert 'results' in response.data

        assert response.data['results']['code'] == '200'

    # @pytest.mark.django_db
    # @pytest.mark.parametrize(
    #     "test_input,expected",
    #     [
    #         ({'first_name': 'test', 'last_name': 'test'}, )
    #     ]
    # )
    # def test_update_password_with_wrong_right_should_not_work(self, client_api, single_user_without_group, test_input, expected):
    #     client_api.force_authenticate(user=single_user_without_group)
    #     body = {}
    #     response = client_api.post(self.url, data=body, format='json')
    #     assert response.status_code == 403
    #     assert response.data['detail'] == 'You do not have permission to perform this action.'


@pytest.mark.user_space
class TestRetrieve:
    url = '/api/users/'

    @pytest.mark.django_db
    def test_unauthenticated_user_should_not_work(self, client_api, single_user_without_group):
        response = client_api.get(
            self.url+f'{str(single_user_without_group.id)}/')

        assert response.status_code == 403
        assert response.data['detail'] == 'Authentication credentials were not provided.'

    @pytest.mark.django_db
    def test_not_admin_or_not_staff_user_should_not_work(self, client_api, single_user_without_group):
        client_api.force_authenticate(user=single_user_without_group)
        response = client_api.get(
            self.url+f'{str(single_user_without_group.id)}/')

        assert response.status_code == 403
        assert response.data['detail'] == 'You do not have permission to perform this action.'

    @pytest.mark.django_db
    def test_retrieve_existent_user_should_work(self, client_api, admin_user, mocker):
        client_api.force_authenticate(user=admin_user)
        mocker.patch('apis.users.space.UserInfoSerializer',
                     UserInfoSerializer(admin_user))
        response = client_api.get(self.url+f'{str(admin_user.id)}/')

        assert response.status_code == 200
        assert response.data['data']['id'] == str(admin_user.id)
        assert response.data['data']['username'] == admin_user.username

    @pytest.mark.django_db
    def test_retrieve_non_existent_user_should_work(self, client_api, admin_user, mocker):
        client_api.force_authenticate(user=admin_user)
        response = client_api.get(
            self.url+f'cbb5e191-f0f5-4bfc-bbcb-16017c3a65e4/')

        assert response.status_code == 500
        assert response.data['message'] == 'No User matches the given query.'
        assert response.data['code'] == '500'


@pytest.mark.user_space
class TestUpdate:
    url = '/api/users/'

    @pytest.mark.django_db
    def test_unauthenticated_user_should_not_work(self, client_api, single_user_without_group):
        body = {}
        response = client_api.put(
            self.url+f'{str(single_user_without_group.id)}/', data=body, format='json')

        assert response.status_code == 403
        assert response.data['detail'] == 'Authentication credentials were not provided.'

    @pytest.mark.django_db
    def test_not_admin_or_not_staff_user_should_not_work(self, client_api, single_user_without_group):
        body = {}
        client_api.force_authenticate(user=single_user_without_group)
        response = client_api.put(
            self.url+f'{str(single_user_without_group.id)}/', data=body, format='json')

        assert response.status_code == 403
        assert response.data['detail'] == 'You do not have permission to perform this action.'

    @pytest.mark.django_db
    def test_update_non_existent_user_should_not_work(self, client_api, admin_user, mocker):
        client_api.force_authenticate(user=admin_user)

        body = {}
        response = client_api.put(
            self.url+f'cbb5e191-f0f5-4bfc-bbcb-16017c3a65e4/', data=body, format='json')

        assert response.status_code == 500
        assert response.data['message'] == 'No User matches the given query.'
        assert response.data['code'] == '500'

    @pytest.mark.django_db
    def test_update_with_existing_username_should_not_work(self, client_api, admin_user):
        client_api.force_authenticate(user=admin_user)
        body = {'first_name': 'test', 'username': admin_user.username}
        response = client_api.post(self.url, data=body, format='json')

        assert response.status_code == 400
        assert 'username' in response.data['message']
        assert 'user with this username already exists.' in str(
            response.data['message'])

    @pytest.mark.django_db
    def test_update_with_existing_email_should_not_work(self, client_api, admin_user):
        client_api.force_authenticate(user=admin_user)
        body = {'first_name': 'test', 'email': admin_user.email}
        response = client_api.post(self.url, data=body, format='json')

        assert response.status_code == 400
        assert 'email' in response.data['message']
        assert 'user with this email already exists.' in str(
            response.data['message'])

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "test_input,expected_status",
        [
            ({'first_name': 'John', 'last_name': 'Spensor'}, 201),
            ({'first_name': 'John', 'last_name': 'Spensor',
              'enterprise': 'Something'}, 201)
        ]
    )
    def test_update_existent_user_should_work(self, client_api, admin_user, test_input, expected_status):
        client_api.force_authenticate(user=admin_user)
        response = client_api.put(
            self.url+f'{str(admin_user.id)}/', data=test_input, format='json')

        assert response.status_code == expected_status
        assert response.data['data']['id'] == str(admin_user.id)
        assert response.data['data']['username'] == admin_user.username


@pytest.mark.user_space
class TestDelete:
    url = '/api/users/'

    @pytest.mark.django_db
    def test_unauthenticated_user_should_not_work(self, client_api, single_user_without_group):
        response = client_api.delete(
            self.url+f'{str(single_user_without_group.id)}/')

        assert response.status_code == 403
        assert response.data['detail'] == 'Authentication credentials were not provided.'

    @pytest.mark.django_db
    def test_not_admin_or_not_staff_user_should_not_work(self, client_api, single_user_without_group):
        client_api.force_authenticate(user=single_user_without_group)
        response = client_api.delete(
            self.url+f'{str(single_user_without_group.id)}/')

        assert response.status_code == 403
        assert response.data['detail'] == 'You do not have permission to perform this action.'

    @pytest.mark.django_db
    def test_delete_non_existent_user_should_not_work(self, client_api, admin_user, mocker):
        client_api.force_authenticate(user=admin_user)

        response = client_api.delete(
            self.url+f'cbb5e191-f0f5-4bfc-bbcb-16017c3a65e4/')

        assert response.status_code == 500
        assert response.data['message'] == 'No User matches the given query.'
        assert response.data['code'] == '500'

    @pytest.mark.django_db
    def test_delete_existent_should_work(self, client_api, admin_user, list_users_instances):
        client_api.force_authenticate(user=admin_user)

        response = client_api.delete(
            self.url+f'{str(list_users_instances[0].id)}/')

        assert response.status_code == 202
        assert response.data['message'] == 'User deleted successfully'
        assert response.data['code'] == '202'


@pytest.mark.user_space
class TestChangePassword:
    url = '/api/users/'

    @pytest.mark.django_db
    def test_unauthenticated_user_should_not_work(self, client_api, single_user_without_group):
        body = {}
        response = client_api.post(
            self.url+f'{str(single_user_without_group.id)}/change_password/', data=body, format='json')

        assert response.status_code == 403
        assert response.data['detail'] == 'Authentication credentials were not provided.'

    @pytest.mark.django_db
    def test_non_existent_user_should_not_work(self, client_api, admin_user):
        client_api.force_authenticate(user=admin_user)

        body = {}
        response = client_api.post(
            self.url+f'cbb5e191-f0f5-4bfc-bbcb-16017c3a65e4/change_password/', data=body, format='json')

        assert response.status_code == 500
        assert response.data['message'] == 'No User matches the given query.'
        assert response.data['code'] == '500'

    @pytest.mark.django_db
    def test_non_admin_or_non_staff_needs_field_old_password(self, client_api, single_user_without_group):
        client_api.force_authenticate(user=single_user_without_group)

        body = {"new_password": "mike2"}
        response = client_api.post(
            self.url+f'{str(single_user_without_group.id)}/change_password/', data=body, format='json')

        assert response.status_code == 400
        assert response.data['code'] == '400'
        assert 'old_password' in response.data['message']
        assert response.data['message']['old_password'] == [
            'This field is required.']

    @pytest.mark.django_db
    def test_non_admin_or_non_staff_typing_wrong_password_should_not_work(self, client_api, single_user_without_group):
        client_api.force_authenticate(user=single_user_without_group)

        body = {"old_password": "mikeeee", "new_password": "mike2"}
        response = client_api.post(
            self.url+f'{str(single_user_without_group.id)}/change_password/', data=body, format='json')

        assert response.status_code == 400
        assert 'Incorrect current Password' in str(response.data['message'])
        assert response.data['code'] == '400'

    @pytest.mark.django_db
    def test_non_admin_or_non_staff_should_change_his_own_password(self, client_api, single_user_without_group):
        client_api.force_authenticate(user=single_user_without_group)

        body = {"old_password": "mike", "new_password": "mike2"}
        response = client_api.post(
            self.url+f'{str(single_user_without_group.id)}/change_password/', data=body, format='json')

        assert response.status_code == 200
        assert response.data['message'] == 'Password successfully updated'
        assert response.data['code'] == '200'

    @pytest.mark.django_db
    def test_admin_or_staff_user_does_not_need_field_old_password(self, client_api, admin_user, single_user_without_group):
        client_api.force_authenticate(user=admin_user)

        body = {"new_password": "mike2"}
        response = client_api.post(
            self.url+f'{str(single_user_without_group.id)}/change_password/', data=body, format='json')

        assert response.status_code == 200
        assert response.data['message'] == 'Password successfully updated'
        assert response.data['code'] == '200'

    @pytest.mark.django_db
    def test_admin_or_staff_should_update_any_user_password_without_old_password_field(self, client_api, admin_user, single_user_without_group):
        client_api.force_authenticate(user=admin_user)

        body = {"new_password": "mike2"}
        response = client_api.post(
            self.url+f'{str(single_user_without_group.id)}/change_password/', data=body, format='json')

        assert response.status_code == 200
        assert response.data['message'] == 'Password successfully updated'
        assert response.data['code'] == '200'


@pytest.mark.user_space
class TestMe:
    url = '/api/users/connected_user/'

    def test_unauthenticated_user_should_not_work(self,  client_api):
        response = client_api.get(self.url, format='json')

        assert response.status_code == 403
        assert response.data['detail'] == 'Authentication credentials were not provided.'

    @pytest.mark.django_db
    def test_authenticated_user_should_work(self,  client_api, single_user_without_group):
        client_api.force_authenticate(user=single_user_without_group)
        response = client_api.get(self.url, format='json')

        assert response.status_code == 200
        assert response.data['id'] == str(single_user_without_group.id)
