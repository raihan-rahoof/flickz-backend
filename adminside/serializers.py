from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from user_auth.models import User
from .models import Movie
from theatre_side.models import Theatre

#-------------Authenticating of admin----------------------------------
class AdminLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    class Meta:
        model = User
        fields = ['email', 'password']

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(email=email, password=password)

            if not user:
                raise serializers.ValidationError('Invalid credentials')

            if not user.is_superuser:
                raise serializers.ValidationError('User is not a superuser')

            # Generate tokens
            refresh = RefreshToken.for_user(user)
            access = str(refresh.access_token)

            return {
                'email': user.email,
                'name': user.get_full_name,
                'access_token': str(access),
                'refresh_token': str(refresh)
            }
        else:
            raise serializers.ValidationError('Both email and password are required')



class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','email','first_name','last_name','phone','is_active']



#------------------Movie side serialisers--------------------------
class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'

    def create(self , validated_data):
        title = validated_data.get('title')
        language = validated_data.get('language')
        genre = validated_data.get('genre')

        existing_movie = Movie.objects.filter(title=title, language=language, genre=genre)


        if existing_movie:
            raise serializers.ValidationError("Movie with this title and language already exists")
        
        return super().create(validated_data)


#-----------------------Theatre side serialisers----------------------------------
class UserSerialiser(serializers.ModelSerializer):
    class Meta:
        model=User
        fields = ['email']


class ThatreListSerializer(serializers.ModelSerializer):
    user = UserSerialiser(read_only = True)
    class Meta:
        model = Theatre
        fields = '__all__'
