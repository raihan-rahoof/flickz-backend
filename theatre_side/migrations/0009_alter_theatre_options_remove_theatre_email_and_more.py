# Generated by Django 4.1.2 on 2024-06-02 08:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('theatre_side', '0008_alter_shows_date_alter_shows_end_time_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='theatre',
            options={'verbose_name': 'Theatre Profile', 'verbose_name_plural': 'Theatre Profiles'},
        ),
        migrations.RemoveField(
            model_name='theatre',
            name='email',
        ),
        migrations.RemoveField(
            model_name='theatre',
            name='groups',
        ),
        migrations.RemoveField(
            model_name='theatre',
            name='is_superuser',
        ),
        migrations.RemoveField(
            model_name='theatre',
            name='last_login',
        ),
        migrations.RemoveField(
            model_name='theatre',
            name='user_permissions',
        ),
        migrations.AddField(
            model_name='theatre',
            name='user',
            field=models.OneToOneField(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='theatre_profile', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
