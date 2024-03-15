from celery import shared_task
from django.core.mail import send_mail
from django.utils.html import format_html
from .models import Purchase, Payment
from django.utils.timezone import now
from datetime import timedelta
from django.db.models import Max
from django.db.models import OuterRef, Subquery
@shared_task
def send_reminder_emails():
    subject = 'Alert: Purchase Remaining Balance'
    from_email = 'setting email'
    recipient_list = ['user send email']
    email_body_lines = []

    reminder_threshold = now() -  timedelta(days=30)

    # Subquery to get the latest payment for each buyer
    latest_payments_subquery = Subquery(
        Payment.objects.filter(
            purchase=OuterRef('pk')
        ).order_by('-balance_paid_date', '-pk')  # Orders by balance_paid_date first, then by pk to break ties
        .values('balance_paid_date')[:1]
    )

    # Subquery to get the latest balance amount for each buyer
    latest_balance_subquery = Subquery(
        Payment.objects.filter(
            purchase=OuterRef('pk')
        ).order_by('-balance_paid_date', '-pk')  # Orders by balance_paid_date first, then by pk to break ties
        .values('balance_amount')[:1]
    )

    purchases = Purchase.objects.annotate(
        latest_payment_date=latest_payments_subquery,
        latest_balance_amount=latest_balance_subquery
    ).filter(
        latest_payment_date__lte=reminder_threshold,
        latest_balance_amount__gt=0
    )

    for purchase in purchases:
        # Construct the email line for this buyer
        last_payment_date = purchase.latest_payment_date.strftime('%Y-%m-%d') if purchase.latest_payment_date else "N/A"
        amount_paid = purchase.total_purchased_amount - purchase.latest_balance_amount
        balance_amount = purchase.latest_balance_amount
        buyer_name = purchase.buyer_name.name
        buyer_address = purchase.buyer_name.address
        buyer_phone = purchase.buyer_name.phone_number
        email_body_lines.append(
            format_html(
                "<p><strong>Buyer Name:</strong> {}<br>"
                "<strong>Address:</strong> {}<br>"
                "<strong>Phone:</strong> {}<br>"
                "<strong>Category:</strong> {}<br>"
                "<strong>Last Payment Date:</strong> {}<br>"
                "<strong>Total Amount:</strong> {}<br>"
                "<strong>Total Amount Paid:</strong> {}<br>"
                "<strong>Remaining Amount:</strong> {}</p>",
                buyer_name, buyer_address, buyer_phone, purchase.category,
                last_payment_date, purchase.total_purchased_amount, amount_paid, balance_amount
            )
        )

    if email_body_lines:
        message = (
                "<html><body>"
                "<p>Hello, here is the list of customers who have not made a payment for more than 30 days:</p>"
                + "\n".join(email_body_lines) +
                "</body></html>"
        )
        send_mail(subject, message, from_email, recipient_list, html_message=message)
