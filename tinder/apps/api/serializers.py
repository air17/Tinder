from django.contrib.auth import get_user_model
from rest_framework.fields import CharField, DecimalField
from rest_framework.serializers import ModelSerializer
from .models import UserProfile


class ProfileSerializer(ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ("id", "full_name", "avatar", "contact", "about", "distance")

    distance = DecimalField(read_only=True, max_digits=5, decimal_places=1)


class ThinProfileSerializer(ProfileSerializer):
    class Meta:
        model = UserProfile
        fields = ("id", "avatar", "full_name", "distance")


class LocationSerializer(ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ("latitude", "longitude")


class ProfileRegistrationSerializer(ModelSerializer):
    class Meta:
        model = UserProfile
        fields = "__all__"


class UserSerializer(ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("username", "password")

    password = CharField(write_only=True)

    @staticmethod
    def create(validated_data):
        user = get_user_model().objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
        )

        return user
