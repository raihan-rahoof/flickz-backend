# Generated by Django 4.1.2 on 2024-05-07 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminside', '0003_movie_cover'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='duration',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
