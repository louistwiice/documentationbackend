import pytest
from django.contrib.auth.models import Group

from docs.models import Version


@pytest.mark.version  # To mark a Test with a Name. So that we can run it by "pytest -m <group_name>/version"
class TestCreate:
    url = '/api/docs/versions/'

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
    @pytest.mark.parametrize(
        "test_input",
        [
            {'name': 'v 1'},  # Should not contain space
            {'name': 'version!'},
            {'name': 'version"'},
            {'name': 'version/'},
            {'name': 'version.'},
        ]
    )
    def test_create_can_not_contain_special_character_in_name_field(self, client_api, admin_user, test_input):
        client_api.force_authenticate(user=admin_user)
        response = client_api.post(self.url, data=test_input, format='json')

        assert response.status_code == 400
        assert response.data['code'] == '400'
        assert 'name' in response.data['message']
        assert 'Name can not contains special characters or space' in str(response.data['message'])

    @pytest.mark.django_db
    def test_create_should_return_name_in_title_format(self, client_api, admin_user):
        client_api.force_authenticate(user=admin_user)
        body = {'name': 'version1'}
        response = client_api.post(self.url, data=body, format='json')

        assert response.status_code == 201
        assert response.data['code'] == '201'
        assert response.data['data']['name'] == body['name'].title()
        assert response.data['data']['description'] is None

    @pytest.mark.django_db
    def test_name_should_be_unique(self, client_api, admin_user, single_doc_version):
        client_api.force_authenticate(user=admin_user)
        body = {'name': single_doc_version[0].name.lower()}
        response = client_api.post(self.url, data=body, format='json')

        assert response.status_code == 500
        assert str(response.data['message']) == 'UNIQUE constraint failed: docs_version.name'

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "test_input",
        [
            {'name': 'v1', 'description': None},
            {'name': 'version3', 'description': 'simple description'},
        ]
    )
    def test_create_with_good_params_should_work_and_group_should_be_created(self, client_api, admin_user, test_input):
        client_api.force_authenticate(user=admin_user)
        response = client_api.post(self.url, data=test_input, format='json')

        assert response.status_code == 201
        assert response.data['code'] == '201'
        assert response.data['data']['name'] == test_input['name'].title()
        assert response.data['data']['description'] == test_input['description']
        assert response.data['data']['permission']['codename'] == test_input['name'].lower()

        assert Group.objects.filter(name=response.data['data']['name']).first() is not None


@pytest.mark.version
class TestList:
    url = '/api/docs/versions/'

    def test_unauthenticated_user_should_not_work(self, client_api):
        response = client_api.post(self.url)

        assert response.status_code == 403
        assert response.data['detail'] == 'Authentication credentials were not provided.'

    @pytest.mark.django_db
    def test_list_with_any_connected_user_should_work(self, client_api, single_user_without_group, single_doc_version):
        client_api.force_authenticate(user=single_user_without_group)
        response = client_api.get(self.url)

        assert response.status_code == 200


@pytest.mark.version
class TestRetrieve:
    url = '/api/docs/versions/'

    def test_unauthenticated_user_should_not_work(self, client_api):
        response = client_api.post(self.url)

        assert response.status_code == 403
        assert response.data['detail'] == 'Authentication credentials were not provided.'

    @pytest.mark.django_db
    def test_retrieve_with_any_connected_should_return_500_if_he_has_not_permission(self, client_api, single_user_without_group, single_doc_version):
        client_api.force_authenticate(user=single_user_without_group)
        response = client_api.get(self.url+f'{single_doc_version[0].id}/')

        assert response.status_code == 500
        assert response.data['message'] == 'No Version matches the given query.'


    @pytest.mark.django_db
    def test_retrieve_with_any_connected_user_should_work_if_he_has_permission(self, client_api, single_user_with_group, single_doc_version, mocker):
        client_api.force_authenticate(user=single_user_with_group)
        response = client_api.get(self.url+f'{single_doc_version[0].id}/')

        mocker.patch(
            'src.apis.docs.version.VersionViewSet.get_queryset',
            return_value=single_doc_version
        )
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_retrieve_non_existent_docs_version_should_not_work(self, client_api, single_user_without_group, single_doc_version):
        client_api.force_authenticate(user=single_user_without_group)
        response = client_api.get(self.url+f'{single_doc_version[0].id+1}/')

        assert response.status_code == 500
        assert response.data['code'] == '500'
        assert response.data['message'] == 'No Version matches the given query.'


@pytest.mark.version
class TestUpdate:
    url = '/api/docs/versions/'

    @pytest.mark.django_db
    def test_unauthenticated_user_should_not_work(self, client_api, single_doc_version, single_group):
        body = {}
        response = client_api.put(self.url+f'{single_doc_version[0].id+1}/', data=body, format='json')

        assert response.status_code == 403
        assert response.data['detail'] == 'Authentication credentials were not provided.'

    @pytest.mark.django_db
    def test_not_admin_or_not_staff_user_should_not_work(self, client_api, single_user_without_group, single_doc_version):
        client_api.force_authenticate(user=single_user_without_group)
        body = {}
        response = client_api.put(self.url+f'{single_doc_version[0].id+1}/', data=body, format='json')

        assert response.status_code == 403
        assert response.data['detail'] == 'You do not have permission to perform this action.'

    @pytest.mark.django_db
    def test_update_non_existent_docs_version_should_not_work(self, client_api, admin_user, single_doc_version):
        client_api.force_authenticate(user=admin_user)
        body = {}
        response = client_api.put(self.url+f'{single_doc_version[0].id+1}/', data=body, format='json')

        assert response.status_code == 500
        assert response.data['code'] == '500'
        assert response.data['message'] == 'No Version matches the given query.'

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "test_input",
        [
            {'name': 'v1', 'description': None},
            {'name': 'v1', 'description': 'simple description'},
            {'name': 'v122222', 'description': 'simple description'},
        ]
    )
    def test_update_with_good_params_should_work(self, client_api, admin_user, test_input, single_doc_version, single_group):
        client_api.force_authenticate(user=admin_user)
        response = client_api.put(self.url+f'{single_doc_version[0].id}/', data=test_input, format='json')

        assert response.status_code == 201
        assert response.data['code'] == '201'
        assert response.data['data']['name'] == test_input['name'].title()
        assert response.data['data']['description'] == test_input['description']
        assert response.data['data']['permission']['codename'] == test_input['name'].lower()


@pytest.mark.version
class TestDestroy:
    url = '/api/docs/versions/'

    @pytest.mark.django_db
    def test_unauthenticated_user_should_not_work(self, client_api, single_doc_version):
        response = client_api.delete(self.url+f'{single_doc_version[0].id+1}/')

        assert response.status_code == 403
        assert response.data['detail'] == 'Authentication credentials were not provided.'

    @pytest.mark.django_db
    def test_not_admin_or_not_staff_user_should_not_work(self, client_api, single_user_without_group, single_doc_version):
        client_api.force_authenticate(user=single_user_without_group)
        response = client_api.delete(self.url+f'{single_doc_version[0].id+1}/')

        assert response.status_code == 403
        assert response.data['detail'] == 'You do not have permission to perform this action.'

    @pytest.mark.django_db
    def test_delete_non_existent_docs_version_should_not_work(self, client_api, admin_user, single_doc_version):
        client_api.force_authenticate(user=admin_user)
        response = client_api.delete(self.url+f'{single_doc_version[0].id+1}/')

        assert response.status_code == 500
        assert response.data['code'] == '500'
        assert response.data['message'] == 'No Version matches the given query.'

    @pytest.mark.django_db
    def test_delete_existent_should_work(self, client_api, admin_user, single_doc_version, single_group):
        client_api.force_authenticate(user=admin_user)

        response = client_api.delete(self.url+f'{single_doc_version[0].id}/')

        assert response.status_code == 202
        assert response.data['message'] == 'Documentation Version deleted successfully'
        assert response.data['code'] == '202'


@pytest.mark.version
class TestPages:
    url = '/api/docs/versions/'

    @pytest.mark.django_db
    def test_unauthenticated_user_should_not_work(self, client_api, single_doc_version):
        response = client_api.get(self.url+f'{single_doc_version[0].id+1}/pages/')

        assert response.status_code == 403
        assert response.data['detail'] == 'Authentication credentials were not provided.'

    @pytest.mark.django_db
    def test_with_admin_or_staff_should_work(self, client_api, admin_user, list_pages):
        client_api.force_authenticate(user=admin_user)

        response = client_api.get(self.url+f'{list_pages[0].version.id}/pages/')

        assert response.status_code == 200
        assert response.data['results']['code'] == '200'
        assert len(response.data['results']['data']) == len(list_pages)
        assert response.data['results']['data'][0]['id'] == list_pages[0].id

    @pytest.mark.django_db
    def test_with_specific_user_should_not_work_if_he_is_not_in_group(self, client_api, single_user_without_group, list_pages):
        client_api.force_authenticate(user=single_user_without_group)
        response = client_api.get(self.url+f'{list_pages[0].version.id}/pages/')

        assert response.status_code == 500
        assert response.data['code'] == '500'
        assert response.data['message'] == 'No Version matches the given query.'

    @pytest.mark.django_db
    def test_with_specific_user_should_work_if_he_is_in_group(self, client_api, single_user_with_group, list_pages):
        client_api.force_authenticate(user=single_user_with_group)
        response = client_api.get(self.url+f'{list_pages[0].version.id}/pages/')

        assert response.status_code == 200
        assert response.data['results']['code'] == '200'
        assert len(response.data['results']['data']) == len(list_pages)
        assert response.data['results']['data'][0]['id'] == list_pages[0].id
