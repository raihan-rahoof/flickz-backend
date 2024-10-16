from rest_framework import serializers
from adminside.models import Movie
from user_auth.models import User
from .models import Review
from theatre_side.models import Shows
from bookings.models import Bookings
from django.core.exceptions import ValidationError
from .utils import analyze_sentiment

class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["id", "movie", "user", "review_text", "sentiment"]

    def validate(self,data):
        user = self.context['request'].user
        movie = data.get("movie")

        shows = Shows.objects.filter(movie=movie)
        booking = Bookings.objects.filter(show__in = shows,user=user,ticket_expiration=True)

        if not booking.exists():
            raise ValidationError(
                "You must have an active booking for this movie to leave a review.And you must watch it"
            )
        return data

    def create(self, validated_data):
        review_text = validated_data.get('review_text')

        validated_data['sentiment'] = analyze_sentiment(review_text)

        review = Review.objects.create(
            **validated_data
        )

        return review
