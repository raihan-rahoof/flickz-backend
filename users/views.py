from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from datetime import datetime

from adminside.models import Banner, Movie
from adminside.serializers import MovieSerializer
from user_auth.models import User, UserProfile
from bookings.models import Bookings

from .models import Review
from .serializers import BannerListSerialzer, MovieSerializer, ReviewSerializer
from .utils import analyze_sentiment

# Create your views here.


class HomeMovieListView(ListAPIView):
    queryset = Movie.objects.all().order_by("-id")
    serializer_class = MovieSerializer


class MovieDetailsView(RetrieveAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer


class MovieSearchView(APIView):
    def get(self, request):
        query = request.GET.get("q", "")
        if query:
            movies = Movie.objects.filter(title__icontains=query)
            serializer = MovieSerializer(movies, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response([], status=status.HTTP_200_OK)


class BannerListView(ListAPIView):
    queryset = Banner.objects.all()
    serializer_class = BannerListSerialzer


class ReviewCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, movie_id, *args, **kwargs):
        movie = Movie.objects.get(id=movie_id)
        review_text = request.data.get("review_text")
        booking_id = request.data.get("booking_id")
        if not booking_id:
            raise ValidationError('Booking id is Required not found')

        try:
            booking = Bookings.objects.get(id=booking_id)
        except Bookings.DoesNotExist:
            raise ValidationError('Booking with this Id does not exist')

        if not booking.ticket_expiration:
            raise ValidationError('You can only write review after watching the movie')

        show = booking.show
        show_datetime = datetime.combine(show.date,show.end_time)

        if show_datetime < timezone.now():
            raise ValidationError('You can only write review after watching the movie')

        sentiment = analyze_sentiment(review_text)

        review = Review.objects.create(
            user=request.user, movie=movie, review_text=review_text, sentiment=sentiment
        )
        review.save()

        return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)

    def get(self, request, movie_id, *args, **kwargs):
        movie = Movie.objects.get(id=movie_id)
        reviews = movie.reviews.all()

        serializer = ReviewSerializer(reviews, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
