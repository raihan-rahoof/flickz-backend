from django.db import models

# Create your models here.
class Movie(models.Model):
    title = models.CharField(max_length=255,null=True,blank=True)
    poster = models.ImageField(upload_to='posters/',null=True,blank=True)
    cover_image = models.ImageField(upload_to='covers/',null=True,blank=True)
    trailer_link = models.URLField(null=True,blank=True)
    duration = models.CharField(max_length=100,null=True,blank=True)
    cast = models.CharField(max_length=255,null=True,blank=True)
    genre = models.CharField(max_length=100,null=True,blank=True)
    language = models.CharField(max_length=40,null=True,blank=True)
    certificate = models.CharField(max_length=100,null=True,blank=True)
    release_date = models.DateField(null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    

    def __str__(self):
        return self.title