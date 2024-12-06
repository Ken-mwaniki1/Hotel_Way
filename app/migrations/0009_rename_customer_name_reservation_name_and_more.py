# Generated by Django 4.2.16 on 2024-11-25 20:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_order_created_at_order_customer_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='reservation',
            old_name='customer_name',
            new_name='name',
        ),
        migrations.RemoveField(
            model_name='reservation',
            name='date_reserved',
        ),
        migrations.RemoveField(
            model_name='reservation',
            name='guest',
        ),
        migrations.RemoveField(
            model_name='reservation',
            name='room',
        ),
        migrations.RemoveField(
            model_name='reservation',
            name='status',
        ),
        migrations.AddField(
            model_name='reservation',
            name='email',
            field=models.EmailField(max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='reservation',
            name='num_guests',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='reservation',
            name='room_type',
            field=models.CharField(choices=[('single', 'Single'), ('double', 'Double'), ('suite', 'Suite')], default='single', max_length=10),
        ),
        migrations.AddField(
            model_name='reservation',
            name='special_requests',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='check_in_date',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='check_out_date',
            field=models.DateField(null=True),
        ),
    ]
