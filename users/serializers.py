from rest_framework import serializers
from adminside.models import Movie
from user_auth.models import User


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'

