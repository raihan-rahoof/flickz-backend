from datetime import datetime

from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from adminside.models import Movie
from adminside.serializers import MovieSerializer
from bookings.models import Bookings
from user_auth.models import User, UserProfile


from .serializers import MovieSerializer,ReviewSerializer
from .utils import analyze_sentiment
from .pagination import MoviePagination


class HomeMovieListView(ListAPIView):
    queryset = Movie.objects.all().order_by("-id")
    serializer_class = MovieSerializer
    pagination_class = MoviePagination


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


class MovieReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request,movie_id):
        try:
            movie = Movie.objects.filter(id=movie_id)
        except Movie.DoesNotExist:
            return Response({'error':'Movie Doesnt Exist'},status=status.HTTP_404_NOT_FOUND)

        serializer = ReviewSerializer(
            data={**request.data, "movie": movie.id, "user": request.user.id}
        )
        serializer.is_valid(raise_exception=True)

        review = serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
