# Generated by Django 5.0.2 on 2024-02-28 11:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_payment_balance_paid_date_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='payment',
            old_name='balance_amount_paid',
            new_name='new_payment',
        ),
        migrations.RemoveField(
            model_name='purchase',
            name='amount_paid',
        ),
        migrations.RemoveField(
            model_name='purchase',
            name='balance_amount',
        ),
        migrations.AddField(
            model_name='payment',
            name='amount_paid',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='balance_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='payment',
            name='balance_paid_date',
            field=models.DateField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='purchase',
            name='address',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='purchase',
            name='material',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.product'),
        ),
    ]