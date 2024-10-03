from rest_framework import serializers
from adminside.models import Movie
from user_auth.models import User
from .models import Review

class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'

class UserForReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','first_name','last_name','email']

class MovieForReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ['id','title','language']

class ReviewSerializer(serializers.ModelSerializer):
    user = UserForReviewSerializer
    movie = MovieForReviewSerializer
    booking_id = serializers.IntegerField()

    class Meta:
        model = Review
        fields = ['id','user','movie','review_text','sentiment','booking_id']
