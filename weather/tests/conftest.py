import pytest
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    """Fixture for creating an instance of APIClient for making API requests."""
    return APIClient()


@pytest.fixture
def api_client_with_authenticated_user(db, api_client, create_user):
    """Fixture for creating an authenticated API client."""
    user = create_user(email='test_user@example.com')
    api_client.force_authenticate(user=user)
    yield api_client
    api_client.force_authenticate(user=None)


@pytest.fixture
def subscription(db, api_client_with_authenticated_user):
    """Fixture for creating a subscription object in the test database."""
    url = reverse('new_subscription')
    data = {
        "city": {
            "name": "Wroclaw",
            "state": "",
            "country_code": "PL"
        },
        "notification_frequency": 2
    }
    api_client_with_authenticated_user.post(url, data, format='json')
