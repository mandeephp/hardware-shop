from datetime import datetime

from django.contrib import admin
from django.contrib.admin.utils import unquote
from django.core.mail import send_mail
from django.contrib.admin.widgets import AdminFileWidget
from django.utils.html import format_html
from django.db import models
import nested_admin
from django.db.models import DateField
from django.db.models.functions import Trunc
from .models import Category, Purchase, Payment, Bill, Buyer
from django import forms
from django.contrib.admin import SimpleListFilter
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from phonenumber_field.widgets import PhoneNumberInternationalFallbackWidget
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.forms import TextInput, Textarea
from django.forms.models import BaseInlineFormSet


class PaymentInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Don't filter out existing payments if you want them to show up
        # self.queryset = Payment.objects.none()  # This line should be commented out or adjusted


class CustomAdminFileWidget(AdminFileWidget):
    def render(self, name, value, attrs=None, renderer=None):
        result = []
        if value and hasattr(value, "url"):
            result.append(
                f'''<a href="{value.url}" target="_blank">
                      <img 
                        src="{value.url}" alt="{value}" 
                        width="500" height="500"
                        style="object-fit: cover;"
                      />
                    </a>'''
            )
        result.append(super().render(name, value, attrs, renderer))
        return format_html("".join(result))


# Define an inline for Payments so we can edit them within the Purchase inline
class PaymentInline(nested_admin.NestedTabularInline):
    model = Payment
    formset = PaymentInlineFormSet

    fields = (
        'new_payment', 'payment_type', 'other_payment_text', 'amount_paid', 'balance_amount',
        'get_total_purchased_amount',
        'balance_paid_date')
    readonly_fields = ('amount_paid', 'balance_amount', 'get_total_purchased_amount', 'balance_paid_date')
    extra = 0

    def get_total_purchased_amount(self, obj):
        if obj.purchase:  # Make sure the payment is linked to a buyer
            return obj.purchase.total_purchased_amount
        return None  # Return None or 0 if there is no related buyer

    get_total_purchased_amount.short_description = 'Total Purchased Amount'

    # You may need to ensure that 'get_total_purchased_amount' is also included in 'readonly_fields' if it's


class PurchaseInline(nested_admin.NestedStackedInline):
    model = Purchase
    extra = 0  # Number of extra forms to display
    inlines = [PaymentInline]  # Nest PaymentInline within PurchaseInline
    fields = ('buyer_name', 'category', 'purchase_slip', 'purchase_date', 'total_purchased_amount',)

    formfield_overrides = {
        models.ImageField: {'widget': CustomAdminFileWidget},
        models.CharField: {'widget': TextInput(attrs={'size': '20'})},
        models.TextField: {'widget': Textarea(attrs={'rows': 4, 'cols': 40})},
    }

    def display_purchase_slip(self, obj):
        if obj.purchase_slip:
            return format_html('<img src="{}" width="300" height="300" style="object-fit: cover;"/>',
                               obj.purchase_slip.url)
        return "-"

    display_purchase_slip.short_description = 'Purchase Slip'
    def get_formset(self, request, obj=None, **kwargs):
        formset = super(PurchaseInline, self).get_formset(request, obj, **kwargs)
        # Additional logic to include purchase date in the formset
        return formset

# Register your models here.

def grant_permissions_to_user(username, model_names):
    # Find the user
    user = User.objects.get(username=username)
    if user.is_staff and not user.is_superuser:
        # Get content types for the specified models
        content_types = ContentType.objects.filter(Q(app_label='accounts', model__in=model_names))

        # Get permissions for view, add, and change
        permissions = Permission.objects.filter(
            content_type__in=content_types,
            codename__in=['add_category', 'change_category', 'view_category',
                          'add_product', 'change_product', 'view_product',
                          'add_purchase', 'change_purchase', 'view_purchase',
                          'add_payment', 'change_payment', 'view_payment',
                          'add_bill', 'change_bill', 'view_bill', ]
        )

        # Grant permissions to the user
        user.user_permissions.set(permissions)


@receiver(user_logged_in)
def grant_permissions(sender, user, request, **kwargs):
    # Check if the user is staff and not a superuser
    if user.is_staff and not user.is_superuser:
        # Check if the user already has permissions
        if not user.has_perms(['accounts.add_category', 'accounts.change_category', 'accounts.view_category',
                               'accounts.add_product', 'accounts.change_product', 'accounts.view_product',
                               'accounts.add_purchase', 'accounts.change_purchase', 'accounts.view_purchase',
                               'accounts.add_payment', 'accounts.change_payment', 'accounts.view_payment',
                               'accounts.add_bill', 'accounts.change_bill', 'accounts.view_bill', ]):
            # If the user doesn't have permissions, grant them
            grant_permissions_to_user(user, ['category', 'product', 'buyer', 'payment', 'bill'])
class CustomPhoneNumberWidget(PhoneNumberInternationalFallbackWidget):
    def format_value(self, value):
        if value:
            formatted_number = value.as_e164  # Get E.164 formatted number
            return f"+{formatted_number[1:3]} {formatted_number[3:8]} {formatted_number[8:13]} {formatted_number[13:]}"
        return ''


class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ('buyer_name', 'category', 'purchase_slip', 'purchase_date','total_purchased_amount',)


class CategoryFilter(SimpleListFilter):
    title = 'Category'
    parameter_name = 'category'

    def lookups(self, request, model_admin):
        # Get all distinct categories from the payments
        categories = Purchase.objects.values_list('category__name', flat=True).distinct()
        return tuple((category, category) for category in categories)

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(category__name=self.value())
        else:
            None


class PaymentInline(admin.TabularInline):
    model = Payment
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    readonly_fields = ('amount_paid', 'balance_amount', 'get_total_purchased_amount', 'balance_paid_date')
    extra = 1
    can_delete = False

    def get_total_purchased_amount(self, obj):
        return obj.purchase.total_purchased_amount

    get_total_purchased_amount.short_description = 'Total Purchased Amount'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by('-id')

    def has_change_permission(self, request, obj=None):
        # If obj is None, it means it's in the creation stage, so allow changes
        if obj is None:
            return True
        return False

    def get_max_num(self, request, obj=None, **kwargs):
        if obj:
            payments = obj.payment_set.all()
            for payment in payments:
                if payment.amount_paid == payment.purchase.total_purchased_amount and payment.balance_amount == 0:
                    return 0  # Do not show extra fields if any payment meets the condition
        return super().get_max_num(request, obj=obj, **kwargs)


class PurchaseAdmin(admin.ModelAdmin):
    form = PurchaseForm
    change_form_template = 'admin/accounts/buyer/change_form.html'
    inlines = [PaymentInline]
    list_display = ('buyer_name', 'category', 'total_purchased_amount', 'purchase_date', 'pdf_button')
    search_fields = ['buyer_name']
    list_filter = (CategoryFilter,)
    formfield_overrides = {  # Here
        models.ImageField: {"widget": CustomAdminFileWidget}
    }
    date_hierarchy = 'purchase_date'

    actions = ['send_email']

    class Media:
        js = ('admin/js/purchase_form.js',)

    def display_purchase_slip(self, obj):
        if obj.purchase_slip:
            return format_html('<img src="{}" width="300" height="300" />', obj.purchase_slip.url)
        return "-"

    display_purchase_slip.short_description = 'Purchase Slip'

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return [inline(self.model, self.admin_site) for inline in self.inlines]

    def send_email(self, request, queryset):
        subject = 'Alert Purchase Remaining Balance'
        from_email = 'email'
        recipient_list = ['send to email']
        email_body_lines = []

        for purchase in queryset:
            payments = purchase.payment_set.order_by('-payment_date', '-pk')  # Order by date and then by primary key
            last_payment = payments.first()

            if last_payment:
                last_payment_date = last_payment.payment_date.strftime('%Y-%m-%d')
                amount_paid = last_payment.amount_paid
                balance_amount = last_payment.balance_amount
                payment_received = last_payment.payment_received
            else:
                last_payment_date = "No payments made"
                amount_paid = "N/A"
                balance_amount = "N/A"
                payment_received = "N/A"

            email_body_lines.append(
                format_html(
                    "<p><strong>Buyer Name:</strong> {}<br>"
                    "<strong>Address:</strong> {}<br>"
                    "<strong>Phone:</strong> {}<br>"
                    "<strong>Category:</strong> {}<br>"
                    "<strong>Last Payment Date:</strong> {}<br>"
                    "<strong>Total Amount:</strong> {}<br>"
                    "<strong>Total Amount Paid:</strong> {}<br>"
                    "<strong>Remaining Amount:</strong> {}<br>"
                    "<strong>Last Payment Received:</strong> {}</p>",
                    purchase.buyer_name, purchase.address, purchase.phone_number, purchase.category, last_payment_date,
                    purchase.total_purchased_amount, amount_paid, balance_amount, payment_received
                )
            )

        message = (
                "<html><body>"
                "<p>Hello, here is the list of customer who did not paid from last 30 days:</p>"
                + "\n".join(email_body_lines) +
                "</body></html>"
        )

        # Send the HTML-formatted email
        send_mail(subject, message, from_email, recipient_list, html_message=message)

        # Optionally, inform the user in the admin interface
        self.message_user(request, 'Email with buyer remaining balances sent successfully.')

    send_email.short_description = 'Send Email with Remaining Balances'

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        else:
            return False

    def pdf_button(self, obj):
        url = reverse('generate_pdf', args=[obj.id])
        return mark_safe(
            '<button style="background-color:#417690;"><a href="{}" target="_blank" style="color:#fff";>Generate PDF</a></button>'.format(
                url))

    pdf_button.allow_tags = True
    pdf_button.short_description = 'Download PDF'


class BuyerCategoryFilter(admin.SimpleListFilter):
    title = 'Category'
    parameter_name = 'category'

    def lookups(self, request, model_admin):
        # Get all distinct category names from purchases associated with buyers
        categories = Category.objects.distinct().values_list('id', 'name')
        return [(category[0], category[1]) for category in categories]

    def queryset(self, request, queryset):
        if self.value():
            # Filter buyers by purchases made in the selected category
            return queryset.filter(purchase__category__id=self.value())
class PurchaseDateFilter(SimpleListFilter):
    title = 'Purchase Date'
    parameter_name = 'purchase_date'

    def lookups(self, request, model_admin):
        # Return a list of tuples. Each tuple is a pair: (query_string, verbose_name)
        # This is where you generate the date options for the filter
        dates = Purchase.objects.dates('purchase_date', 'day').order_by('-purchase_date')
        return [(date.strftime('%Y-%m-%d'), date.strftime('%Y-%m-%d')) for date in dates]

    def queryset(self, request, queryset):
        # This is where you filter the queryset based on the selected date
        if self.value():
            date_selected = datetime.strptime(self.value(), '%Y-%m-%d')
            return queryset.filter(purchase__purchase_date=date_selected)
        return queryset

class BuyerAdmin(nested_admin.NestedModelAdmin):
    inlines = [PurchaseInline]
    list_display = ('name', 'address', 'phone_number', 'create_at')
    search_fields = ['name', 'address', 'phone_number']
    list_filter = ['create_at',  BuyerCategoryFilter, PurchaseDateFilter]  # Add your new filter here
    change_form_template = 'admin/accounts/buyer/change_form.html'

    class Media:
        js = ('admin/js/purchase_form.js',)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        buyer = self.get_object(request, unquote(object_id))

        # Get unique purchase dates using `Trunc` to truncate the datetime to a date
        unique_dates = Purchase.objects.filter(buyer_name=buyer).annotate(
            date=Trunc('purchase_date', 'day', output_field=DateField())
        ).values_list('date', flat=True).distinct().order_by('-date')

        # Pass the unique dates to the template
        extra_context['unique_dates'] = unique_dates
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def get_inline_instances(self, request, obj=None):
        # Custom method to modify the inline instances
        inline_instances = []
        if obj is not None:
            for inline_class in self.inlines:
                inline = inline_class(self.model, self.admin_site)
                if request:
                    if not (inline.has_view_or_change_permission(request) or
                            inline.has_add_permission(request) or
                            inline.has_delete_permission(request)):
                        continue
                    if not inline.has_add_permission(request,obj):
                        inline.max_num = 0
                inline_instances.append(inline)
        return inline_instances
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if 'purchase_date' in request.GET:
            purchase_date = request.GET['purchase_date']
            qs = qs.filter(purchase__purchase_date=purchase_date)
        return qs

admin.site.register(Category)
admin.site.register(Purchase, PurchaseAdmin)
admin.site.register(Bill)
admin.site.register(Buyer, BuyerAdmin)