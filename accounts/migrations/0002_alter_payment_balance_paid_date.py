# Generated by Django 5.0.2 on 2024-02-28 06:35

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='balance_paid_date',
            field=models.DateField(default=datetime.date.today),
        ),
    ]