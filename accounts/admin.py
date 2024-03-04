from django.contrib import admin
from .models import Category, Purchase, Payment, Product
from django import forms
from django.contrib.admin import SimpleListFilter
from django.http import HttpResponse

# Register your models here.


class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'product_category', 'price')
    search_fields=('product_name',)

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['material'].queryset = Product.objects.none()

        if 'category' in self.data:
            try:
                category_id = int(self.data.get('category'))
                self.fields['material'].queryset = Product.objects.filter(product_category_id=category_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.category:
            self.fields['material'].queryset = self.instance.category.product_set

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
        
class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 1
    readonly_fields = ('amount_paid', 'balance_amount','get_total_purchased_amount', 'balance_paid_date')
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
        # Otherwise, do not allow changes to existing objects
        return False
    
class PurchaseAdmin(admin.ModelAdmin):
    form = PurchaseForm
    change_form_template = 'admin/accounts/purchase/change_form.html'
    inlines = [PaymentInline]
    list_display = ('buyer_name', 'address', 'category', 'total_purchased_amount', 'purchase_date')
    readonly_fields = ('total_purchased_amount', 'get_product_price')
    search_fields = ['buyer_name']
    list_filter = (CategoryFilter,)

    class Media:
        js = ('admin/js/purchase_form.js',)
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  
            return self.readonly_fields + ('quantity',)
        return self.readonly_fields
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return [inline(self.model, self.admin_site) for inline in self.inlines]

    def get_product_price(self, obj):  
            return obj.material.price
    get_product_price.short_description = 'Product Price'
    
    
    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True  # Superuser can delete
        else:
            return False 
    
class PaymentAdmin(admin.ModelAdmin):
    model = Payment
    list_display = ('get_buyer_name', 'get_address', 'get_category','amount_paid',
                    'new_payment','balance_amount' ,'get_total_purchased_amount', 'balance_paid_date')
    

    readonly_fields = ('amount_paid', 'balance_amount')
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # If the object exists (i.e., it's being edited)
            return self.readonly_fields + ('new_payment',)
        return self.readonly_fields
    
    def get_buyer_name(self, obj):
        return obj.purchase.buyer_name
    get_buyer_name.short_description = 'Buyer Name'
    
    def get_address(self, obj):
        return obj.purchase.address
    get_address.short_description = 'Address'

    def get_category(self, obj):
        return obj.purchase.category
    get_category.short_description = 'Category'

    def get_total_purchased_amount(self, obj):
        return obj.purchase.total_purchased_amount
    get_total_purchased_amount.short_description = 'Total Purchased Amount'
    
    
admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(Purchase, PurchaseAdmin)
