from django.db import models
from datetime import date
from django.db.models import Sum, F, Value as V, ExpressionWrapper, Case, When
from django.db.models.functions import Coalesce
from django.contrib.auth.models import Permission

# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name

class Product(models.Model):
    product_category = models.ForeignKey(Category, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=200)
    price = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.product_name} - {self.product_category}"
    
class Purchase(models.Model):
    buyer_name = models.CharField(max_length=200)
    address = models.CharField(max_length=200, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    material = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.IntegerField()
    purchase_date = models.DateField(auto_now_add=True)
    total_purchased_amount = models.IntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.material and self.quantity:
            self.total_purchased_amount = self.material.price * self.quantity
            self.category = self.material.product_category
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.buyer_name} - {self.category} - {self.total_purchased_amount}"

    
class Payment(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE)
    amount_paid = models.IntegerField(null=True, blank=True)
    balance_amount = models.IntegerField( null=True, blank=True)
    new_payment = models.IntegerField(null=True, blank=True)
    balance_paid_date = models.DateField(auto_now=True)

    def save(self, *args, **kwargs):
        # Calculate the total amount paid including initial payment and new payments
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
    

    
    
    
    