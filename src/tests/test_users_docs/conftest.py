import pytest
from django.contrib.auth.models import Permission
from model_bakery import baker
from django.contrib.auth.models import Group
from rest_framework.test import APIClient

from users.models import User
from docs.models import Version, Page, Part


@pytest.fixture
def client_api():
    return APIClient()


@pytest.fixture
def inactivated_user():
   user = baker.make(User, username='inactive', email='inactive@mail.com',  is_staff=False, is_superuser=False, is_active=False)
   user.set_password('inactive')
   user.save()
   return user


@pytest.fixture
def single_user_without_group():
   user = baker.make(User, is_staff=False, is_superuser=False)
   user.set_password('mike')
   user.save()
   return user


@pytest.fixture
def single_user_with_group():
   user = baker.make(User, is_staff=False, is_superuser=False)
   user.set_password('mike')
   user.save()
   group = baker.make(Group, _quantity=1, name='Version1')[0]
   group.user_set.add(user)
   group.permissions.add(
      baker.make(Permission, _quantity=1, id=37)[0]
   )
   group.permissions.add(
      baker.make(Permission, _quantity=1, id=38)[0]
   )
   group.permissions.add(
      baker.make(Permission, _quantity=1, id=39)[0]
   )
   return user


@pytest.fixture
def single_user_with_group():
   user = baker.make(User, is_staff=False, is_superuser=False)
   user.set_password('mike')
   user.save()
   group = baker.make(Group, _quantity=1, name='Version1')[0]
   group.user_set.add(user)
   group.permissions.add(
      baker.make(Permission, _quantity=1, id=37)[0]
   )
   group.permissions.add(
      baker.make(Permission, _quantity=1, id=38)[0]
   )
   group.permissions.add(
      baker.make(Permission, _quantity=1, id=39)[0]
   )
   return user


@pytest.fixture
def single_doc_version():
   perm = baker.make(Permission, _quantity=1, id=37)[0]

   version = baker.make(Version, _quantity=1, name='Version1', permission=perm)
   return version


@pytest.fixture
def single_permission():
   permission = baker.make(Permission, _quantity=1,)
   return permission


@pytest.fixture
def list_pages():
   version_perm = baker.make(Permission, _quantity=1, id=37)[0]

   version = baker.make(Version, _quantity=1, name='Version1', permission=version_perm)
   pages = baker.make(Page, _quantity=1, version=version[0], permission=baker.make(Permission, _quantity=1)[0])
   return pages


@pytest.fixture
def list_parts():
   version = baker.make(
      Version, _quantity=1, name='Version1',
      permission=baker.make(Permission, _quantity=1, id=37)[0]
   )[0]
   page = baker.make(
      Page, _quantity=1, version=version,
      permission=baker.make(Permission, _quantity=1, id=38)[0]
   )[0]

   parts = baker.make(
      Part, _quantity=1,
      page=page,
      permission=baker.make(Permission, _quantity=1, id=39)[0]
   )
   return parts


@pytest.fixture
def list_parts_with_other_perms():
   version = baker.make(
      Version, _quantity=1, name='Version1',
      permission=baker.make(Permission, _quantity=1, id=50)[0]
   )[0]
   page = baker.make(
      Page, _quantity=1, version=version,
      permission=baker.make(Permission, _quantity=1, id=51)[0]
   )[0]

   parts = baker.make(
      Part, _quantity=1,
      page=page,
      permission=baker.make(Permission, _quantity=1, id=52)[0]
   )
   return parts


@pytest.fixture
def other_perms():
   permission= baker.make(Permission, _quantity=3,)
   return permission


@pytest.fixture
def single_group():
   group = baker.make(Group, _quantity=1, name='Version1')
   return group

