import pytest
import json
from django.urls import reverse


@pytest.mark.django_db(reset_sequences=True)
def test_new_subscription(api_client_with_authenticated_user):
    """Test creating a new subscription."""
    url = reverse('new_subscription')
    data = {
        "city": {
            "name": "Wroclaw",
            "state": "",
            "country_code": "PL"
        },
        "notification_frequency": 2
    }

    response = api_client_with_authenticated_user.post(url, data, format='json')
    response_json = json.loads(response.content)
    assert response.status_code == 201
    assert response_json['res'] == 'New subscription created successfully'


@pytest.mark.django_db(reset_sequences=True)
def test_new_subscription_city_not_exist(api_client_with_authenticated_user):
    """Test creating a new subscription with a city that does not exist."""
    url = reverse('new_subscription')
    data = {
        "city": {
            "name": "wrong-city",
            "state": "",
            "country_code": "UA"
        },
        "notification_frequency": 2
    }

    response = api_client_with_authenticated_user.post(url, data, format='json')
    response_json = json.loads(response.content)
    assert response.status_code == 404
    assert response_json['error'] == 'city not found'


@pytest.mark.django_db(reset_sequences=True)
def test_new_subscription_already_subscribed(api_client_with_authenticated_user, subscription):
    """Test creating a new subscription for a city to which the user is already subscribed."""
    url = reverse('new_subscription')
    data = {
        "city": {
            "name": "Wroclaw",
            "state": "",
            "country_code": "PL"
        },
        "notification_frequency": 2
    }

    response = api_client_with_authenticated_user.post(url, data, format='json')
    response_json = json.loads(response.content)
    assert response.status_code == 400
    assert response_json['error'] == 'You are already subscribed to this city. Please, edit an existing subscription'


@pytest.mark.django_db(reset_sequences=True)
def test_get_subscriptions_list(api_client_with_authenticated_user, subscription):
    """Test retrieving the list of user subscriptions."""
    url_subscriptions_list = reverse('subscriptions_list')
    subscriptions_list = [{'id': 1,
                           'city':
                               {'name': 'Wroclaw', 'state': '', 'country_code': 'PL'},
                           'notification_frequency': 2}]
    response = api_client_with_authenticated_user.get(url_subscriptions_list)
    response_json = json.loads(response.content)
    assert response.status_code == 200
    assert response_json == subscriptions_list


@pytest.mark.django_db(reset_sequences=True)
def test_edit_subscription(api_client_with_authenticated_user, subscription):
    """Test editing an existing subscription."""
    url_subscriptions_list = reverse('subscriptions_list')
    response = api_client_with_authenticated_user.get(url_subscriptions_list)
    subscriptions_list = json.loads(response.content)

    url = reverse('subscription_action', kwargs={'id': 1})
    data = {
        "city": {
            "name": "Wroclaw",
            "state": "",
            "country_code": "PL"
        },
        "notification_frequency": 7
    }
    response = api_client_with_authenticated_user.put(url, data, format='json')
    response_json = json.loads(response.content)
    assert response.status_code == 200
    assert response_json['res'] == "Subscription edited"

    url_subscriptions_list = reverse('subscriptions_list')
    response = api_client_with_authenticated_user.get(url_subscriptions_list)
    response_json = json.loads(response.content)
    data['id'] = 1
    assert data in response_json


@pytest.mark.django_db(reset_sequences=True)
def test_delete_subscription(api_client_with_authenticated_user, subscription):
    """Test deleting a subscription."""
    url = reverse('subscription_action', kwargs={'id': 1})
    response = api_client_with_authenticated_user.delete(url)
    response_json = json.loads(response.content)
    assert response.status_code == 200
    assert response_json['res'] == "Subscription deleted"


@pytest.mark.django_db(reset_sequences=True)
def test_delete_subscription_fail(api_client_with_authenticated_user, subscription):
    """Test failing to delete a subscription that does not exist."""
    url = reverse('subscription_action', kwargs={'id': 2})
    response = api_client_with_authenticated_user.delete(url)
    response_json = json.loads(response.content)
    assert response.status_code == 404
    assert response_json['res'] == "Subscription with id=2 does not exist for this user"
