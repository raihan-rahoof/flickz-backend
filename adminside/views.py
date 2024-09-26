from django.shortcuts import render
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import AdminLoginSerializer , UserListSerializer,MovieSerializer,ThatreListSerializer,AdminDashboardSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from user_auth.models import User
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView
from .models import Movie
from theatre_side.models import Theatre
# Create your views here.

# -------------user side [authentication , block and unblock , also Listing users]---------

class AdminTokenObtainPairView(TokenObtainPairView):
    serializer_class = AdminLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        return Response(data, status=status.HTTP_200_OK)


class UserListView(generics.ListAPIView):
        queryset = User.objects.filter(is_superuser=False,user_type='normal')
        serializer_class = UserListSerializer
        permission_classes = [IsAdminUser]


class BlockUnblockUser(APIView):
     def put(self,request,id):
        try:
            user = User.objects.get(pk=id)
        except User.DoesNotExist:
             return Response({'error':'user not found'},status=status.HTTP_404_NOT_FOUND)
        
        user.is_active = not user.is_active
        user.save()
        serializer = UserListSerializer(user)
        return Response(serializer.data,status=status.HTTP_200_OK)


# --------------------movies section [movie adding , updating , deleting]------------------------


class MovieListCreateAPIView(generics.ListCreateAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception = True)

        title = serializer.validated_data.get('title')
        language = serializer.validated_data.get('language')
        genre = serializer.validated_data.get('genre')

        existing_movie = Movie.objects.filter(title=title , language = language , genre=genre)

        if existing_movie:
             return Response({'error':'Movie with same Name,Language,Genre already exists'})
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class MovieupdateView(generics.RetrieveUpdateDestroyAPIView):
     queryset=Movie.objects.all()
     serializer_class = MovieSerializer
     lookup_field = 'pk'
     permission_classes = [IsAdminUser]


# ----------------Theatre Side views--------------

class TheatreListView(generics.ListAPIView):
     queryset=Theatre.objects.all()
     serializer_class = ThatreListSerializer
     permission_classes = [IsAdminUser]

class TheatreRequestsView(generics.ListAPIView):
     queryset = Theatre.objects.filter(is_verified=True, admin_allow=False)
     serializer_class = ThatreListSerializer
     permission_classes = [IsAdminUser]

class TheatreDetailView(generics.RetrieveAPIView):
     queryset=Theatre.objects.all()
     serializer_class = ThatreListSerializer
     lookup_field = 'pk'
     permission_classes = [IsAdminUser]


class ApproveTheatreView(APIView):
    permission_classes=[IsAdminUser]

    def patch(self,request,theatre_id,*args,**kwargs):
        try:
            theatre = Theatre.objects.get(id=theatre_id)

            if theatre.admin_allow:
                return Response({"message": f"Theatre '{theatre.theatre_name}' is already approved."}, 
                                status=status.HTTP_400_BAD_REQUEST)
            theatre.admin_allow = True
            theatre.is_verified = True
            theatre.is_active = True

            theatre.save()

            return Response({"message": f"Theatre '{theatre.theatre_name}' has been approved."}, 
                            status=status.HTTP_200_OK)

        except Theatre.DoesNotExist:
            return Response(
                {"error": "Theatre not found."}, status=status.HTTP_404_NOT_FOUND
            )


class DisapproveTheatreView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, theatre_id,*args,**kwargs):
        try:
            
            theatre = Theatre.objects.get(id=theatre_id)

            

            
            theatre.admin_allow = False
            theatre.is_verified = False
            theatre.is_active = False
            theatre.save()

            # Return success message
            return Response(
                {"message": f"Theatre '{theatre.theatre_name}' has been disapproved."},
                status=status.HTTP_200_OK,
            )

        except Theatre.DoesNotExist:
            return Response(
                {"error": "Theatre not found."}, status=status.HTTP_404_NOT_FOUND
            )


class AdminDashboardView(APIView):
    permission_classes=[IsAdminUser]
    def get(self,request,*args,**kwargs):
        total_users = User.objects.count()
        total_theatres = Theatre.objects.count()
        total_movies = Movie.objects.count()
        blocked_users = User.objects.filter(is_active=False).count()

        data = {
            "total_users": total_users,
            "total_theatres": total_theatres,
            "total_movies": total_movies,
            "blocked_users": blocked_users,
        }

        serializer = AdminDashboardSerializer(data)
        return Response(serializer.data)
