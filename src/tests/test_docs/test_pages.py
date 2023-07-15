import pytest
from django.contrib.auth.models import Group, Permission

from docs.models import Version, Page


@pytest.mark.page
class TestCreate:
    url = '/api/docs/pages/'

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
    def test_version_is_always_required(self, client_api, admin_user):
        client_api.force_authenticate(user=admin_user)
        body = {'name': 'senelec'}
        response = client_api.post(self.url, data=body, format='json')

        assert response.status_code == 400
        assert response.data['code'] == '400'
        assert response.data['message']['version'][0] == 'This field is required.'

    @pytest.mark.django_db
    def test_version_should_exist_first(self, client_api, admin_user):
        client_api.force_authenticate(user=admin_user)
        body = {'name': 'senelec', 'version': 1}
        response = client_api.post(self.url, data=body, format='json')

        assert response.status_code == 400
        assert response.data['code'] == '400'
        assert 'object does not exist' in str(response.data['message'])

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "test_input",
        [
            {'name': 'senelec', 'description': None, 'version': 1},
            {'name': 'senelec', 'description': 'A simple desription', 'version': 1},
        ]
    )
    def test_creations_should_work_perfectly(self, client_api, admin_user, single_doc_version, single_group, test_input, mocker):
        client_api.force_authenticate(user=admin_user)

        mocker.patch.object(Version.objects, 'get', return_value=single_doc_version[0], autospec=True)
        mocker.patch.object(Group.objects, 'get', return_value=single_group[0], autospec=True)

        response = client_api.post(self.url, data=test_input, format='json')

        assert response.status_code == 201
        assert response.data['code'] == '201'
        assert response.data['data']['name'] == test_input['name'].title()
        assert response.data['data']['description'] == test_input['description']
        assert response.data['data']['version'] == test_input['version']
        assert response.data['data']['permission'] is not None


@pytest.mark.page
class TestRetrieve:
    url = '/api/docs/pages/'

    def test_unauthenticated_user_should_not_work(self, client_api):
        response = client_api.get(self.url+f'1/')

        assert response.status_code == 403
        assert response.data['detail'] == 'Authentication credentials were not provided.'

    @pytest.mark.django_db
    def test_non_existent_page_should_not_work(self, client_api, admin_user, list_pages):
        client_api.force_authenticate(user=admin_user)
        body = {}
        response = client_api.put(self.url+f'{list_pages[0].id+30}/', data=body, format='json')

        assert response.status_code == 500
        assert response.data['code'] == '500'
        assert response.data['message'] == 'No Page matches the given query.'

    @pytest.mark.django_db
    def test_admin_or_staff_should_work(self, client_api, admin_user, list_pages):
        client_api.force_authenticate(user=admin_user)
        response = client_api.get(self.url+f'{list_pages[0].id}/')

        assert response.status_code == 200
        assert response.data['data']['id'] == list_pages[0].id

    @pytest.mark.django_db
    def test_non_admin_or_non_staff_can_not_retrieve_if_he_is_not_in_group_version(self, client_api, single_user_without_group, list_pages):
        client_api.force_authenticate(user=single_user_without_group)
        response = client_api.get(self.url+f'{list_pages[0].id}/')

        assert response.status_code == 500
        assert response.data['code'] == '500'
        assert response.data['message'] == 'No Page matches the given query.'

    # @pytest.mark.django_db
    # def test_non_admin_or_non_staff_can_retrieve_if_he_is_in_group_version(self, client_api, single_user_with_group, list_pages, mocker):
    #     client_api.force_authenticate(user=single_user_with_group)
    #     response = client_api.get(self.url+f'{list_pages[0].id}/')
    #
    #     mocker.patch.object(
    #         Page.objects,
    #         'filter',
    #         return_value=list_pages
    #     )
    #     # assert response.status_code == 200
    #     # assert response.data['code'] == '200'
    #     # assert response.data['data']['id'] == list_pages[0].id
    #     # assert response.data['data']['description'] == list_pages[0].description
    #     # assert response.data['data']['version'] == list_pages[0].version.id
    #
    #
    #     assert response.data['message'] == list_pages[0].version.id


@pytest.mark.page
class TestUpdate:
    url = '/api/docs/pages/'

    @pytest.mark.django_db
    def test_unauthenticated_user_should_not_work(self, client_api, list_pages):
        body = {}
        response = client_api.put(self.url+f'{list_pages[0].id+1}/', data=body, format='json')

        assert response.status_code == 403
        assert response.data['detail'] == 'Authentication credentials were not provided.'

    @pytest.mark.django_db
    def test_not_admin_or_not_staff_user_should_not_work(self, client_api, single_user_without_group, list_pages):
        client_api.force_authenticate(user=single_user_without_group)
        body = {}
        response = client_api.put(self.url+f'{list_pages[0].id+1}/', data=body, format='json')

        assert response.status_code == 403
        assert response.data['detail'] == 'You do not have permission to perform this action.'

    @pytest.mark.django_db
    def test_update_only_description_should_work(self, client_api, admin_user, list_pages):
        client_api.force_authenticate(user=admin_user)
        body = {'description': 'a description'}
        response = client_api.put(self.url+f'{list_pages[0].id}/', data=body, format='json')

        assert response.status_code == 200
        assert response.data['code'] == '200'
        assert response.data['data']['description'] == body['description']

    @pytest.mark.django_db
    def test_update_name_should_update_permission(self, client_api, admin_user, list_pages, single_permission, mocker):
        client_api.force_authenticate(user=admin_user)
        body = {'name': 'a description'}

        mocker.patch.object(
            Permission.objects,
            'get',
            return_value=single_permission[0]
        )
        response = client_api.put(self.url+f'{list_pages[0].id}/', data=body, format='json')

        assert response.status_code == 200
        assert response.data['code'] == '200'
        assert response.data['data']['name'] == body['name'].title()


@pytest.mark.page
class TestDestroy:
    url = '/api/docs/pages/'

    @pytest.mark.django_db
    def test_unauthenticated_user_should_not_work(self, client_api, list_pages):
        response = client_api.delete(self.url+f'{list_pages[0].id+1}/')

        assert response.status_code == 403
        assert response.data['detail'] == 'Authentication credentials were not provided.'

    @pytest.mark.django_db
    def test_not_admin_or_not_staff_user_should_not_work(self, client_api, single_user_without_group, list_pages):
        client_api.force_authenticate(user=single_user_without_group)
        response = client_api.delete(self.url+f'{list_pages[0].id+100}/')

        assert response.status_code == 403
        assert response.data['detail'] == 'You do not have permission to perform this action.'

    @pytest.mark.django_db
    def test_delete_non_existent_page_should_not_work(self, client_api, admin_user, list_pages):
        client_api.force_authenticate(user=admin_user)
        response = client_api.delete(self.url+f'{list_pages[0].id+1000}/')

        assert response.status_code == 500
        assert response.data['code'] == '500'
        assert response.data['message'] == 'No Page matches the given query.'

    @pytest.mark.django_db
    def test_delete_existent_should_work(self, client_api, admin_user, list_pages, single_permission):
        client_api.force_authenticate(user=admin_user)

        response = client_api.delete(self.url+f'{list_pages[0].id}/')

        assert response.status_code == 202
        assert response.data['message'] == 'Documentation Page deleted successfully'
        assert response.data['code'] == '202'


@pytest.mark.page
class TestParts:
    url = '/api/docs/pages/'

    @pytest.mark.django_db
    def test_unauthenticated_user_should_not_work(self, client_api, single_doc_version):
        response = client_api.get(self.url+f'{single_doc_version[0].id+1}/parts/')

        assert response.status_code == 403
        assert response.data['detail'] == 'Authentication credentials were not provided.'

    @pytest.mark.django_db
    def test_with_admin_or_staff_should_work(self, client_api, admin_user, list_parts):
        client_api.force_authenticate(user=admin_user)

        response = client_api.get(self.url+f'{list_parts[0].page.id}/parts/')

        assert response.status_code == 200
        assert response.data['results']['code'] == '200'
        assert len(response.data['results']['data']) == 1

    @pytest.mark.django_db
    def test_with_specific_user_should_not_work_if_he_is_not_in_any_group(self, client_api, single_user_without_group, list_parts):
        client_api.force_authenticate(user=single_user_without_group)
        response = client_api.get(self.url+f'{list_parts[0].page.id}/parts/')

        assert response.status_code == 500
        assert response.data['code'] == '500'
        assert response.data['message'] == 'No Page matches the given query.'

    # @pytest.mark.django_db
    # def test_with_specific_user_should_not_work_if_he_is_not_in_page_group(self, client_api, single_user_with_group, list_parts_with_other_perms,other_perms, mocker):
    #     client_api.force_authenticate(user=single_user_with_group)
    #
    #     mocker.patch(
    #         'src.apis.docs.page.PageViewSet.get_object',
    #         return_value=list_parts_with_other_perms[0].page
    #     )
    #
    #     mocker.patch.object(
    #         Permission.objects,
    #         'filter',
    #         return_value=other_perms
    #     )
    #
    #     response = client_api.get(self.url+f'{list_parts_with_other_perms[0].page.id}/parts/')
    #
    #     assert response.status_code == 500
    #     assert response.data['code'] == '500'
    #     assert response.data['message'] == 'No Page matches the given query.'
    #

    @pytest.mark.django_db
    def test_with_specific_user_should_work_if_he_is_in_page_group_and_part_group(self, client_api, single_user_with_group, list_parts, mocker):
        client_api.force_authenticate(user=single_user_with_group)

        mocker.patch(
            'src.apis.docs.page.PageViewSet.get_object',
            return_value=list_parts[0].page
        )

        response = client_api.get(self.url+f'{list_parts[0].page.id}/parts/')
        assert response.status_code == 200
