# Generated by Django 4.1.2 on 2024-06-10 05:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('theatre_side', '0014_alter_shows_theatre'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shows',
            name='theatre',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='theatre_side.theatre'),
        ),
    ]
