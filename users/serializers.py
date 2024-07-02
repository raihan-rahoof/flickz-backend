from rest_framework import serializers
from adminside.models import Movie
from user_auth.models import UserProfile

class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'


class MobileVerificaitonSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["is_mobile_verified"]