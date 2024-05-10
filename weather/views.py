from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.utils import json
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from .models import CityName, CityWeather, CustomUser, UserSubscription
from .serializers import (CityNameSerializer, CityWeatherSerializer,
                          OneSubscriptionSerializer, RegistrationSerializer,
                          UserSubscriptionSerializer)

from .utils import get_weather


class RegistrationView(APIView):
    """API endpoint for user registration."""
    queryset = CustomUser.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer

    @extend_schema(description='### Registration: provide your email and create a password, repeat  your password in '
                               '"password2" parameter',
                   tags=['auth'], )
    def post(self, request):
        """Handle POST requests for user registration."""
        request_body = json.loads(request.body)
        serializer = RegistrationSerializer(data=request_body)
        if serializer.is_valid():
            account = serializer.save()
            account.is_active = True
            account.save()
            return Response({"result": "Registered successfully",
                             "user_info": serializer.data},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({'error': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)


class DeleteAccount(APIView):
    """API endpoint for deleting user accounts."""
    permission_classes = (IsAuthenticated,)

    @extend_schema(description='### Delete your account',
                   tags=['auth'], )
    def delete(self, request):
        """Handle DELETE requests for deleting user accounts."""
        user = request.user
        user.delete()

        return Response({"result": "user deleted"}, status=status.HTTP_200_OK)


def validate_serializer(serializer, error_message):
    """Helper function to validate serializer data."""
    if serializer.is_valid():
        serializer.save()
    else:
        return Response({'errors': serializer.errors,
                         'message': error_message},
                        status=status.HTTP_400_BAD_REQUEST)


def remove_unused_entries():
    """Helper function to remove unused city entries."""
    cities = CityName.objects.all()
    for city in cities:
        city_subscriptions = city.subscriptions.all()
        if not city_subscriptions:
            city.delete()


class UserSubscriptionsView(APIView):
    """API endpoint for managing user subscriptions."""
    permission_classes = (IsAuthenticated,)

    @extend_schema(description='### Get the list of all your subscriptions',
                   tags=['subscriptions'], )
    def get(self, request):
        """Handle GET requests for retrieving user subscriptions."""
        user = request.user
        subscriptions = user.subscriptions
        serializer = UserSubscriptionSerializer(subscriptions, many=True)
        for subscriprion in serializer.data:
            subscriprion.pop('user')
            subscriprion.pop('weather_info')
            subscriprion.pop('last_info_update')

            city_id = subscriprion['city']
            city = CityName.objects.get(id=city_id)
            city_info = CityNameSerializer(city)
            subscriprion['city'] = city_info.data

        return Response(serializer.data)


class NewSubscriptionView(APIView):
    """API endpoint for creating new user subscriptions."""
    permission_classes = (IsAuthenticated,)
    serializer_class = OneSubscriptionSerializer

    @extend_schema(description='### Provide data for a new subscription.</br></br>'
                               '"city": name of the city you subscribe to.</br>'
                               '"state": a 2-letter ISO Alpha-2 code. available only for the USA locations. '
                               'if not needed, just leave it blank: <em>state: ""</em>.</br> '
                               '"country_code": a 2-letter ISO Alpha-2 code.</br>'
                               ' "notification_frequency": measured in hours.',
                   tags=['subscriptions'], )
    def post(self, request):
        """Handle POST requests for creating new user subscriptions."""
        request_body = json.loads(request.body)

        city_data = request_body['city']

        weather_data, code = get_weather(city_data)
        if code != 200:
            return Response({'error': weather_data['message'],
                             'code': code},
                            status=status.HTTP_404_NOT_FOUND)

        else:
            if not CityName.objects.filter(name=city_data['name'],
                                           state=city_data['state'],
                                           country_code=city_data['country_code']).exists():
                city_serializer = CityNameSerializer(data=city_data)
                validate_serializer(city_serializer, error_message="city_serializer errors:")

            subscription_city = CityName.objects.get(name=city_data['name'],
                                                     state=city_data['state'],
                                                     country_code=city_data['country_code'])

            if subscription_city.subscriptions.filter(user=request.user).exists():
                return Response({'error': 'You are already subscribed to this city. '
                                          'Please, edit an existing subscription'},
                                status=status.HTTP_400_BAD_REQUEST)

            if not CityWeather.objects.filter(city=subscription_city).exists():
                weather_data['city'] = subscription_city.pk
                city_weather_serializer = CityWeatherSerializer(data=weather_data)
                validate_serializer(city_weather_serializer, error_message="city_weather_serializer errors:")

            subscription_weather = CityWeather.objects.get(city=subscription_city.pk)

            subscription_data = {
                'user': request.user.pk,
                'city': subscription_city.pk,
                'weather_info': subscription_weather.pk,
                'notification_frequency': request_body['notification_frequency'],
            }

            subscription_serializer = UserSubscriptionSerializer(data=subscription_data)
            if subscription_serializer.is_valid():
                subscription_serializer.save()
                return Response({'res': 'New subscription created successfully'}, status=status.HTTP_201_CREATED)
            else:
                return Response(subscription_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubscriptionActionsView(APIView):
    """API endpoint for editing and deleting user subscriptions."""
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return OneSubscriptionSerializer

    def get_usersubscription_object(self, subscription_id):
        """Helper function to get user subscription object by ID."""
        try:
            return UserSubscription.objects.get(id=subscription_id)
        except UserSubscription.DoesNotExist:
            return None

    @extend_schema(description='### Write new updated information about your subscription.</br></br>'
                               '"city": name of the city you subscribe to.</br>'
                               '"state": a 2-letter ISO Alpha-2 code. available only for the USA locations. '
                               'if not needed, just leave it blank: <em>state: ""</em>.</br> '
                               '"country_code": a 2-letter ISO Alpha-2 code.</br>'
                               '"notification_frequency": measured in hours.',
                   tags=['subscriptions'], )
    def put(self, request, id):
        """Handle PUT requests for editing user subscriptions."""
        user = request.user
        user_subscriptions = user.subscriptions.all()
        subscription = self.get_usersubscription_object(subscription_id=id)
        if not subscription or subscription not in user_subscriptions:
            return Response({"res": f"Subscription with id={id} does not exist for this user"},
                            status=status.HTTP_400_BAD_REQUEST,
                            )
        else:
            request_body = json.loads(request.body)
            city_data = request_body['city']

            weather_data, code = get_weather(city_data)
            if code != 200:
                return Response({'error': weather_data['message'],
                                 'code': code},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                # if any field about city has changed
                if not CityName.objects.filter(name=city_data['name'],
                                               state=city_data['state'],
                                               country_code=city_data['country_code']).exists():
                    city_serializer = CityNameSerializer(data=city_data)
                    validate_serializer(city_serializer, error_message="city_serializer errors:")

                subscription_city = CityName.objects.get(name=city_data['name'],
                                                         state=city_data['state'],
                                                         country_code=city_data['country_code'])

                if not CityWeather.objects.filter(city=subscription_city).exists():
                    weather_data['city'] = subscription_city.pk
                    city_weather_serializer = CityWeatherSerializer(data=weather_data)
                    validate_serializer(city_weather_serializer, error_message="city_weather_serializer errors:")

                subscription_weather = CityWeather.objects.get(city=subscription_city.pk)

                new_subscription_data = {
                    'user': request.user.pk,
                    'city': subscription_city.pk,
                    'weather_info': subscription_weather.pk,
                    'notification_frequency': request_body.get('notification_frequency',
                                                               subscription.notification_frequency),
                }

                subscription_serializer = UserSubscriptionSerializer(instance=subscription, data=new_subscription_data,
                                                                     partial=True)
                if subscription_serializer.is_valid():
                    subscription_serializer.save()
                    remove_unused_entries()  # remove cities that nobody is subscribed for
                    return Response({"res": "Subscription edited"}, status=status.HTTP_200_OK)
                else:
                    return Response({"res": subscription_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(description='### Specify the id of the subscription you want to delete',
                   tags=['subscriptions'], )
    def delete(self, request, id):
        """Handle DELETE requests for deleting user subscriptions."""
        user = request.user
        user_subscriptions = user.subscriptions.all()
        subscription = self.get_usersubscription_object(subscription_id=id)
        if not subscription or subscription not in user_subscriptions:
            return Response({"res": f"Subscription with id={id} does not exist for this user"},
                            status=status.HTTP_404_NOT_FOUND,
                            )
        else:
            user.subscriptions.remove(subscription)
            subscription.delete()
            remove_unused_entries()  # remove cities that nobody is subscribed for
            return Response(
                {"res": "Subscription deleted"},
                status=status.HTTP_200_OK
            )
