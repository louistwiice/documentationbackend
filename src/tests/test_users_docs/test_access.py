import pytest
from django.contrib.auth.models import Group


@pytest.mark.access
class TestGroups:
    url = '/api/docs/access/groups/'

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
    def test_should_return_empty_if_there_is_no_version_created(self, client_api, admin_user):
        client_api.force_authenticate(user=admin_user)
        response = client_api.get(self.url)

        assert response.status_code == 200
        assert response.data['results']['data'] == []

    @pytest.mark.django_db
    def test_should_work_if_group_is_found(self, client_api, admin_user, single_group, single_doc_version, mocker):
        client_api.force_authenticate(user=admin_user)

        mocker.patch.object(
            Group.objects,
            'get',
            return_value=single_group[0]
        )
        response = client_api.get(self.url)

        assert response.status_code == 200
        assert response.data['results']['data'][0]['id'] == single_group[0].id
        assert response.data['results']['data'][0]['name'] == single_group[0].name


class TestPermissions:
    url = '/api/docs/access/permissions/'

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
    def test_should_return_empty_if_there_is_no_docs_created(self, client_api, admin_user):
        client_api.force_authenticate(user=admin_user)
        response = client_api.get(self.url)

        assert response.status_code == 200
        assert response.data['data']['versions'].count() == 0  # I don't know why, but it returns a queryset. So we have to use count
        assert response.data['data']['pages'].count() == 0  # I don't know why, but it returns a queryset. So we have to use count
        assert response.data['data']['parts'].count() == 0  # I don't know why, but it returns a queryset. So we have to use count


@pytest.mark.access
class TestGrantUser:
    url = '/api/docs/access/grant_user_permission/'

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
    def test_permission_id_or_user_id_are_required_and_should_exist(self, client_api, admin_user):
        client_api.force_authenticate(user=admin_user)
        body = {'permissions': [1000], 'user': '4fa85f64-5717-4562-b3fc-2c963f66afa6'}
        response = client_api.post(self.url, data=body, format='json')

        assert response.status_code == 400
        assert response.data['code'] == '400'
        assert response.data['message']['permissions'][0] == 'Some ID are not permissions IDs. Please check again'
        assert response.data['message']['user'][0] == 'User ID does not exist'

    @pytest.mark.django_db
    def test_user_with_a_given_permission_should_access_version(self, client_api, admin_user, single_user_without_group, single_doc_version):
        body = {'permissions': [single_doc_version[0].permission.id], 'user': single_user_without_group.id}

        client_api.force_authenticate(user=single_user_without_group)
        response = client_api.get(f'/api/docs/versions/{single_doc_version[0].id}/')
        assert response.status_code == 500
        assert response.data['message'] == 'No Version matches the given query.'

        client_api.force_authenticate(user=admin_user)
        response = client_api.post(self.url, data=body, format='json')

        assert response.status_code == 202
        assert response.data['code'] == '202'
        assert response.data['data']['id'] == str(single_user_without_group.id)
        assert str(single_doc_version[0].permission.id) in str(response.data['data']['user_permissions'])
        assert str(single_doc_version[0].permission.codename) in str(response.data['data']['user_permissions'])

        client_api.force_authenticate(user=single_user_without_group)
        response = client_api.get(f'/api/docs/versions/{single_doc_version[0].id}/')
        assert response.status_code == 200
        assert response.data['code'] == '200'


@pytest.mark.access
class TestDenyUser:
    url = '/api/docs/access/deny_user_permission/'

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
    def test_permission_id_or_user_id_are_required_and_should_exist(self, client_api, admin_user):
        client_api.force_authenticate(user=admin_user)
        body = {'permissions': [1000], 'user': '4fa85f64-5717-4562-b3fc-2c963f66afa6'}
        response = client_api.post(self.url, data=body, format='json')

        assert response.status_code == 400
        assert response.data['code'] == '400'
        assert response.data['message']['permissions'][0] == 'Some ID are not permissions IDs. Please check again'
        assert response.data['message']['user'][0] == 'User ID does not exist'

    @pytest.mark.django_db
    def test_user_with_permission_should_be_removed_easily(self, client_api, admin_user, single_user_with_group, single_doc_version):
        client_api.force_authenticate(user=admin_user)
        body = {'permissions': [single_doc_version[0].permission.id], 'user': single_user_with_group.id}
        response = client_api.post(self.url, data=body, format='json')

        assert response.status_code == 202
        assert response.data['code'] == '202'
        assert response.data['data']['id'] == str(single_user_with_group.id)
        assert str(single_doc_version[0].permission.id) not in str(response.data['data']['user_permissions'])
        assert str(single_doc_version[0].permission.codename) not in str(response.data['data']['user_permissions'])
