# Generated by Django 4.2.16 on 2024-11-25 20:18

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_menuitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 1, 1, 0, 0)),
        ),
        migrations.AddField(
            model_name='order',
            name='customer_name',
            field=models.CharField(default='Unknown', max_length=255),
        ),
    ]
