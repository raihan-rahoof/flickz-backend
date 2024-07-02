from rest_framework.generics import ListAPIView , RetrieveAPIView
from adminside.models import Movie
from .serializers import MovieSerializer,MobileVerificaitonSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from adminside.models import Movie
from adminside.serializers import MovieSerializer
from user_auth.models import UserProfile,User

# Create your views here.

class HomeMovieListView(ListAPIView):
    queryset = Movie.objects.all()
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

class ProfileMobileVerificationHandle(APIView):
    def post(self,request):
        serializer = MobileVerificaitonSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = User.objects.get(id=request.user)
                profile = UserProfile.objects.get(user=user)

                profile.is_mobile_verified=True
                profile.save()
                profile_serializer = MobileVerificaitonSerializer(profile)

                return Response(
                    {
                        "message": "Mobile number verified successfully",
                        "user_profile": profile_serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
            except User.DoesNotExist:
                return Response({'error':"user not found"},status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
