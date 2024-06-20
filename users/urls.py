from django.urls import path
from .views import HomeMovieListView , MovieDetailsView , MovieSearchView


urlpatterns = [
    path("movies/", HomeMovieListView.as_view(), name="home-movie-list"),
    path("movie/<int:pk>/", MovieDetailsView.as_view(), name="movie-detail"),
    path("movies/search/", MovieSearchView.as_view(), name="movie-search"),
]
