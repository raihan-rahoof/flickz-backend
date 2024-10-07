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

from .models import Review
from .serializers import MovieSerializer, ReviewSerializer
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


