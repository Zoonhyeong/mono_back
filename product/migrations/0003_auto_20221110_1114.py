# Generated by Django 2.2.4 on 2022-11-10 11:14

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0002_subscribe_icon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscribe',
            name='start_date',
            field=models.DateField(default=datetime.datetime.now),
        ),
    ]
