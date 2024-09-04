from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from adminside.models import Banner, Movie
from adminside.serializers import MovieSerializer
from user_auth.models import User, UserProfile

from .models import Review
from .serializers import BannerListSerialzer, MovieSerializer,ReviewSerializer
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
    
    def post(self, request, movie_id, *args, **kwargs):
        movie = Movie.objects.get(id=movie_id)
        review_text = request.data.get("review_text")

        sentiment = analyze_sentiment(review_text)

        review = Review.objects.create(user=request.user,movie=movie,review_text = review_text,sentiment=sentiment)
        review.save()
        
        return Response(ReviewSerializer(review).data,status=status.HTTP_201_CREATED)

    def get(self,request,movie_id,*args,**kwargs):
        movie = Movie.objects.get(id =movie_id)
        reviews = movie.reviews.all()

        serializer = ReviewSerializer(reviews,many=True)

        return Response(serializer.data,status=status.HTTP_200_OK)