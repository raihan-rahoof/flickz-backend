from django.db import models
from adminside.models import Movie
from user_auth.models import User

# Create your models here.
class Review(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='reviews')
    movie = models.ForeignKey(Movie,on_delete=models.CASCADE,related_name='reviews')
    review_text = models.TextField()
    sentiment = models.CharField(max_length=25,null=True,blank=True)

    def __str__(self) -> str:
        return f"Review of {self.movie.title} by {self.user.first_name}"