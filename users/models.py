from django.db import models
from adminside.models import Movie
from user_auth.models import User

# Create your models here.
class Review(models.Model):
    user = models.ForeignKey(User, related_name="reviews", on_delete=models.CASCADE,null=True,blank=True)
    movie = models.ForeignKey(Movie,related_name="movies",on_delete=models.CASCADE,null=True,blank=True)
    review_text = models.TextField()
    sentiment = models.CharField(max_length=250,blank=True,null=True)

    def __str__(self) -> str:
        return f"review for {self.movie.title} of {self.user.first_name}"