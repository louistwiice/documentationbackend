import pytest
from model_bakery import baker

from apis.serializers.users import UserInfoSerializer
from users.models import User
from rest_framework.test import APIClient


@pytest.fixture
def client_api():
    return APIClient()


@pytest.fixture
def example_value():
   return 39


@pytest.fixture
def list_users_instances():
   users = baker.make(User, _quantity=4)
   return users


@pytest.fixture
def list_users_serialized():
   users = baker.make(User, _quantity=4)
   return UserInfoSerializer(users, many=True).data


@pytest.fixture
def admin_user_mike():
   mike = baker.make(User, username='mike', email='mike@mail.com')
   mike.set_password('mike')
   mike.save()

   return mike


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
