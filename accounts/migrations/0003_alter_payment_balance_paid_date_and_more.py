# Generated by Django 5.0.2 on 2024-02-28 09:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_payment_balance_paid_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='balance_paid_date',
            field=models.DateField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='purchase',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.category'),
        ),
    ]