from rest_framework import serializers
from adminside.models import Movie,Banner


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'

class BannerListSerialzer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ['image']
