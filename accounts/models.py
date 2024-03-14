from django.db import models
from django.db.models import Sum, F, Value as V, Case, When
from django.db.models.functions import Coalesce
from phonenumber_field.modelfields import PhoneNumberField


class Buyer(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200, null=True, blank=True)
    phone_number = PhoneNumberField(region='IN', null=True, blank=True, unique=True)
    create_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Purchase(models.Model):
    buyer_name = models.ForeignKey(Buyer, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    purchase_date = models.DateField(blank=True, null=True)
    total_purchased_amount = models.IntegerField(null=True, blank=True)
    purchase_slip = models.ImageField(upload_to='purchase_slips/', null=True, blank=True)

    def __str__(self):
        return f"{self.buyer_name.name} - {self.category} - {self.total_purchased_amount}"


class Payment(models.Model):
    PAYMENT_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('upi', 'UPI'),
        ('cash', 'Cash'),
        ('cheque', 'Cheque'),
        ('other', 'Other'),
    ]
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE)
    amount_paid = models.IntegerField(null=True, blank=True)
    balance_amount = models.IntegerField(null=True, blank=True)
    new_payment = models.IntegerField(null=True, blank=True)
    balance_paid_date = models.DateField(auto_now=True, blank=True, null=True)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_CHOICES, null=True, blank=True)
    other_payment_text = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        total_paid = self.purchase.payment_set.aggregate(
            total_paid=Coalesce(Sum(
                Case(
                    When(new_payment__isnull=False, then=F('new_payment')),
                    default=V(0)
                )
            ), V(0))
        )['total_paid']

        # If there's an initial payment, add it to total_paid
        if self.amount_paid is not None:
            total_paid += self.amount_paid

        # If it's a new payment, add it to the previous total_paid
        if self.new_payment is not None:
            total_paid += self.new_payment

        # Update the amount_paid field with the new total paid amount
        self.amount_paid = total_paid

        # Recalculate the balance_amount
        if self.purchase.total_purchased_amount is not None:
            self.balance_amount = self.purchase.total_purchased_amount - total_paid
        else:
            self.balance_amount = None  # Set balance_amount to None if total_purchased_amount is None

        # Save the updated fields
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.purchase.buyer_name} - {self.new_payment}"


class Bill(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    payment_mode = models.CharField(max_length=200, null=True, blank=True)
    dispatch_through = models.CharField(max_length=200, null=True, blank=True)
    destination = models.CharField(max_length=200, null=True, blank=True)
    vehicle_number = models.CharField(max_length=200, null=True, blank=True)
    transportation = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.purchase.buyer_name}-{self.destination}"