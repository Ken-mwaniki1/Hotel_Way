# Generated by Django 4.2.16 on 2024-11-25 17:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_alter_order_customer_alter_order_guest_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guest',
            name='contact_info',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='guest',
            name='name',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='customer_name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='room',
            name='description',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='room',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='room',
            name='room_type',
            field=models.CharField(max_length=255),
        ),
    ]
