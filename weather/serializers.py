from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password

from .models import CustomUser, CityName, CityWeather, UserSubscription

User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=CustomUser.objects.all())]
    )

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'confirm_password']

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        email = validated_data['email']
        password = validated_data['password']

        existing_user = User.objects.filter(email=email).first()
        if existing_user:
            raise ValidationError("User with this email already exists.")

        user = User.objects.create_user(email=email, password=password)

        return user


class CityNameSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=150)
    state = serializers.CharField(max_length=150, allow_blank=True)
    country_code = serializers.CharField(max_length=2)

    class Meta:
        model = CityName
        fields = ['name', 'state', 'country_code', ]


class CityWeatherSerializer(serializers.ModelSerializer):
    class Meta:
        model = CityWeather
        fields = ['city', 'last_info_update', 'weather_description', 'temperature', 'feels_like',
                  'humidity', 'pressure', 'visibility', 'wind_speed', 'clouds', 'rain', 'snow', ]


class UserSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSubscription
        fields = ['id', 'user', 'city', 'weather_info', 'notification_frequency', 'last_info_update', ]


class OneSubscriptionSerializer(serializers.ModelSerializer):
    city = CityNameSerializer()
    notification_frequency = serializers.IntegerField()

    class Meta:
        model = UserSubscription
        fields = ['city', 'notification_frequency', ]
