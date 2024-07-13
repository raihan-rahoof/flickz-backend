# Generated by Django 5.0.6 on 2024-07-11 05:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0005_alter_bookings_show'),
        ('theatre_side', '0016_alter_shows_theatre'),
    ]

    operations = [
        migrations.CreateModel(
            name='OfflineBookings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('seats', models.JSONField(default=list)),
                ('name', models.CharField(max_length=100)),
                ('email', models.CharField(max_length=100)),
                ('phone', models.CharField(max_length=15)),
                ('seat_number', models.JSONField(default=list)),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_status', models.CharField(max_length=50)),
                ('show', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='offline_bookings', to='theatre_side.shows')),
            ],
        ),
    ]
