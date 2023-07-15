import pytest
from django.contrib.auth.models import Group, Permission

from docs.models import Page


@pytest.mark.part
class TestCreate:
    url = '/api/docs/parts/'

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
    def test_page_is_always_required(self, client_api, admin_user):
        client_api.force_authenticate(user=admin_user)
        body = {'name': 'senelec'}
        response = client_api.post(self.url, data=body, format='json')

        assert response.status_code == 400
        assert response.data['code'] == '400'
        assert response.data['message']['page'][0] == 'This field is required.'

    @pytest.mark.django_db
    def test_page_should_exist_first(self, client_api, admin_user):
        client_api.force_authenticate(user=admin_user)
        body = {'name': 'senelec', 'page': 1}
        response = client_api.post(self.url, data=body, format='json')

        assert response.status_code == 400
        assert response.data['code'] == '400'
        assert 'object does not exist' in str(response.data['message'])

    @pytest.mark.django_db
    def test_page_content_is_required(self, client_api, admin_user, list_parts):
        client_api.force_authenticate(user=admin_user)
        body = {'name': 'senelec', 'page': list_parts[0].page.id}
        response = client_api.post(self.url, data=body, format='json')

        assert response.status_code == 400
        assert response.data['code'] == '400'
        assert response.data['message']['content'][0] == 'This field is required.'

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "test_input,part",
        [
            ({'name': 'senelec', 'content': 'simple content'}, 0),
            #({'name': 'senelec', 'content': 'A simple desription'}, 1),
        ]
    )
    def test_creations_should_work_perfectly(self, client_api, admin_user, single_group, test_input, part, list_parts, mocker):
        client_api.force_authenticate(user=admin_user)

        mocker.patch.object(Page.objects, 'get', return_value=list_parts[part].page, autospec=True)
        mocker.patch.object(Group.objects, 'get', return_value=single_group[0], autospec=True)

        body = test_input
        body['page'] = list_parts[part].page.id
        response = client_api.post(self.url, data=body, format='json')

        assert response.status_code == 201
        assert response.data['code'] == '201'
        assert response.data['data']['name'] == body['name'].title()
        assert response.data['data']['content'] == body['content']
        assert response.data['data']['page'] == body['page']
        assert response.data['data']['permission'] is not None


@pytest.mark.part
class TestRetrieve:
    url = '/api/docs/parts/'

    def test_unauthenticated_user_should_not_work(self, client_api):
        response = client_api.get(self.url+f'1/')

        assert response.status_code == 403
        assert response.data['detail'] == 'Authentication credentials were not provided.'

    @pytest.mark.django_db
    def test_non_existent_page_should_not_work(self, client_api, admin_user, list_parts):
        client_api.force_authenticate(user=admin_user)
        body = {}
        response = client_api.put(self.url+f'{list_parts[0].id+30}/', data=body, format='json')

        assert response.status_code == 500
        assert response.data['code'] == '500'
        assert response.data['message'] == 'No Part matches the given query.'

    @pytest.mark.django_db
    def test_admin_or_staff_should_work(self, client_api, admin_user, list_parts):
        client_api.force_authenticate(user=admin_user)
        response = client_api.get(self.url+f'{list_parts[0].id}/')

        assert response.status_code == 200
        assert response.data['data']['id'] == list_parts[0].id

    @pytest.mark.django_db
    def test_non_admin_or_non_staff_can_not_retrieve_if_he_is_not_in_any_group(self, client_api, single_user_without_group, list_parts):
        client_api.force_authenticate(user=single_user_without_group)
        response = client_api.get(self.url+f'{list_parts[0].id}/')

        assert response.status_code == 500
        assert response.data['code'] == '500'
        assert response.data['message'] == 'No Part matches the given query.'

    @pytest.mark.django_db
    def test_non_admin_or_non_staff_can_not_retrieve_if_he_is_not_in_any_group(self, client_api, single_user_without_group, list_parts):
        client_api.force_authenticate(user=single_user_without_group)
        response = client_api.get(self.url+f'{list_parts[0].id}/')

        assert response.status_code == 500
        assert response.data['code'] == '500'
        assert response.data['message'] == 'No Part matches the given query.'

    @pytest.mark.django_db
    def test_non_admin_or_non_staff_should_if_he_has_group_work(self, client_api, single_user_with_group, list_parts):
        client_api.force_authenticate(user=single_user_with_group)
        response = client_api.get(self.url+f'{list_parts[0].id}/')

        assert response.status_code == 200
        assert response.data['code'] == '200'
        assert response.data['data']['id'] == list_parts[0].id


@pytest.mark.part
class TestUpdate:
    url = '/api/docs/parts/'

    @pytest.mark.django_db
    def test_unauthenticated_user_should_not_work(self, client_api, list_parts):
        body = {}
        response = client_api.put(self.url+f'{list_parts[0].id+1}/', data=body, format='json')

        assert response.status_code == 403
        assert response.data['detail'] == 'Authentication credentials were not provided.'

    @pytest.mark.django_db
    def test_not_admin_or_not_staff_user_should_not_work(self, client_api, single_user_without_group, list_parts):
        client_api.force_authenticate(user=single_user_without_group)
        body = {}
        response = client_api.put(self.url+f'{list_parts[0].id+1}/', data=body, format='json')

        assert response.status_code == 403
        assert response.data['detail'] == 'You do not have permission to perform this action.'

    @pytest.mark.django_db
    def test_update_only_content_should_work(self, client_api, admin_user, list_parts):
        client_api.force_authenticate(user=admin_user)
        body = {'content': 'a description'}
        response = client_api.put(self.url+f'{list_parts[0].id}/', data=body, format='json')

        assert response.status_code == 200
        assert response.data['code'] == '200'
        assert response.data['data']['content'] == body['content']

    @pytest.mark.django_db
    def test_update_name_should_update_permission(self, client_api, admin_user, list_parts, single_permission, mocker):
        client_api.force_authenticate(user=admin_user)
        body = {'name': 'new name'}

        mocker.patch.object(
            Permission.objects,
            'get',
            return_value=single_permission[0]
        )
        response = client_api.put(self.url+f'{list_parts[0].id}/', data=body, format='json')

        assert response.status_code == 200
        assert response.data['code'] == '200'
        assert response.data['data']['name'] == body['name'].title()

    @pytest.mark.django_db
    def test_update_page_should_update_permission(self, client_api, admin_user, list_parts, single_permission, mocker):
        client_api.force_authenticate(user=admin_user)
        body = {'page': list_parts[0].page.id}

        mocker.patch.object(
            Permission.objects,
            'get',
            return_value=single_permission[0]
        )
        response = client_api.put(self.url+f'{list_parts[0].id}/', data=body, format='json')

        assert response.status_code == 200
        assert response.data['code'] == '200'
        assert response.data['data']['page'] == body['page']


@pytest.mark.part
class TestDestroy:
    url = '/api/docs/parts/'

    @pytest.mark.django_db
    def test_unauthenticated_user_should_not_work(self, client_api, list_parts):
        response = client_api.delete(self.url+f'{list_parts[0].id+1}/')

        assert response.status_code == 403
        assert response.data['detail'] == 'Authentication credentials were not provided.'

    @pytest.mark.django_db
    def test_not_admin_or_not_staff_user_should_not_work(self, client_api, single_user_without_group, list_parts):
        client_api.force_authenticate(user=single_user_without_group)
        response = client_api.delete(self.url+f'{list_parts[0].id+100}/')

        assert response.status_code == 403
        assert response.data['detail'] == 'You do not have permission to perform this action.'

    @pytest.mark.django_db
    def test_delete_non_existent_part_should_not_work(self, client_api, admin_user, list_pages):
        client_api.force_authenticate(user=admin_user)
        response = client_api.delete(self.url+f'{list_pages[0].id+1000}/')

        assert response.status_code == 500
        assert response.data['code'] == '500'
        assert response.data['message'] == 'No Part matches the given query.'

    @pytest.mark.django_db
    def test_delete_existent_should_work(self, client_api, admin_user, list_parts, single_permission):
        client_api.force_authenticate(user=admin_user)

        response = client_api.delete(self.url+f'{list_parts[0].id}/')

        assert response.status_code == 202
        assert response.data['message'] == 'Part Page deleted successfully'
        assert response.data['code'] == '202'


