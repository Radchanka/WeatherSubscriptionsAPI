import copy
from celery import shared_task
from datetime import timedelta

from django.core.paginator import Paginator
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
import logging

from .constants import EMAIL_SUBJECT
from .models import CityName, CityWeather, UserSubscription
from .views import get_weather
from .serializers import CityNameSerializer, CityWeatherSerializer, UserSubscriptionSerializer


def update_weather_table():
    """
    Update weather data for all cities.

    Utilizes serializers to retrieve city and weather data,
    then calls the weather data update function for each city.
    """
    all_cities = CityName.objects.all()
    paginator = Paginator(all_cities, 100)
    for page_num in paginator.page_range:
        cities_page = paginator.page(page_num)
        for city in cities_page:
            city_data = CityNameSerializer(city).data
            weather_data, code = get_weather(city_data)
            if code != 200:
                logging.error(f"{weather_data['message']}, 'code': {code}")
            else:
                update_city_weather(city, weather_data)


def update_city_weather(city, weather_data):
    """
    Update weather data for a specific city.

    :param city: The city object.
    :param weather_data: The weather data to update.
    """
    city_weather = CityWeather.objects.get(city=city)
    city_weather_serializer = CityWeatherSerializer(instance=city_weather, data=weather_data, partial=True)
    if city_weather_serializer.is_valid():
        city_weather_serializer.save()
    else:
        logging.error(f"{city_weather_serializer.errors}")


def send_email(weather_data, city_data, user):
    """
    Sends an email with weather report to a user.

    :param weather_data: The weather data.
    :param city_data: The city data.
    :param user: The user object to send the email to.
    """
    weather_data_copy = copy.deepcopy(weather_data)

    del weather_data_copy['city']
    del weather_data_copy['last_info_update']

    email_body = render_to_string('weather/weather_report_template.html', {
        'weather_data': weather_data_copy,  # Sending a copy instead of the original
        'city_data': city_data,
    })
    send_mail(
        subject=EMAIL_SUBJECT,
        message="weather report",
        html_message=email_body,
        from_email=settings.EMAIL_FROM_USER,
        recipient_list=[user.email],
        fail_silently=True,
    )


def update_subscriptions_table():
    """
    Update subscription information and send emails for overdue subscriptions.
    """
    paginator = Paginator(UserSubscription.objects.all(), 100)

    for page_num in range(1, paginator.num_pages + 1):
        page = paginator.page(page_num)

        for subscription in page.object_list:
            time_delta = timezone.now() - subscription.last_info_update
            if time_delta > timedelta(hours=subscription.notification_frequency):
                weather_data = CityWeatherSerializer(subscription.weather_info).data
                city_data = CityNameSerializer(subscription.city).data
                send_email(weather_data=weather_data, city_data=city_data, user=subscription.user)
                new_data = {
                    'last_info_update': timezone.now(),
                }
                subscription_serializer = UserSubscriptionSerializer(instance=subscription, data=new_data, partial=True)
                if subscription_serializer.is_valid():
                    subscription_serializer.save()
                else:
                    logging.error(f"Error updating subscription: {subscription_serializer.errors}")


@shared_task()
def update_tables_and_send_emails():
    """
    Task to update tables and send emails asynchronously.
    """
    update_weather_table()
    update_subscriptions_table()
