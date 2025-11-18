from django.contrib import admin
from . models import BecomeAVendor, Product, Colour, ContactVendor, Size, ProductRating, OrderItem, Orders, Wishlist, Address, VendorRating, Payments
# Register your models here.

@admin.register(BecomeAVendor)
class BecomeAVendorAdmin(admin.ModelAdmin):
    list_display = ['sub_account_ID', 'company_name', 'company_email', 'company_phone_number', 'company_account_name', 'company_bank', 'company_account_number', 'company_state', 'company_address', 'approved']
    search_fields = ['user__username', 'company_name', 'company_email', 'company_phone_number', 'company_state' ]
    list_display_links = ['sub_account_ID', 'company_name',]

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name','vendor__company_name', 'price', 'stock', 'avg_rating' ]
    search_fields = ['name', 'price', 'vendor__company_name','stock']
    list_filter = ['stock', 'avg_rating']

@admin.register(Colour)
class ColourAdmin(admin.ModelAdmin):
    list_display=['color']


@admin.register(ContactVendor)
class ContactVendorAdmin(admin.ModelAdmin):
    list_display =['name', 'email', 'vendor__company_name', 'message']
    search_fields = ['name', 'email']

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ['sizes']


@admin.register(ProductRating)
class ProductRatingAdmin(admin.ModelAdmin):
    list_display = ['product__name','review_stars','avg_rating', 'avg_rating_percentage', 'name', 'email', 'review']
    list_filter= ['review_stars', 'date', 'avg_rating', 'avg_rating_percentage']
    search_fields = ['name', 'email']

@admin.register(VendorRating)
class ProductRatingAdmin(admin.ModelAdmin):
    list_display = ['vendor__company_name','review_stars','avg_rating', 'avg_rating_percentage', 'name', 'email', 'review']
    list_filter= ['review_stars', 'date', 'avg_rating', 'avg_rating_percentage']
    search_fields = ['name', 'email']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['vendor__company_name','product__name', 'user__username', 'ordered', 'quantity', 'size__sizes', 'colour__color']
    search_fields = ['vendor__company_name','product__name',]

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['product__name', 'user__username', 'ordered', 'quantity']
    search_fields = ['product__name',]

@admin.register(Orders)
class OrdersAdmin(admin.ModelAdmin):
    list_display=['vendor__company_name', 'user__username', 'ref_number','total', 'address', 'ordered','vendor_accepted', 'delivered', 'order_date', 'delivered_on']
    search_fields = ['vendor__company_name','user__username', 'total',  'ref_number', 'address']
    list_filter = ['ordered', 'delivered', 'order_date', 'vendor_accepted', 'delivered_on']
    list_display_links = ['vendor__company_name', 'user__username', ]

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user__username','first_name', 'last_name', 'email', 'phone_number', 'state', 'order_notes']
    search_fields = ['email', 'phone_number', 'user__username', 'first_name', 'last_name', ]

@admin.register(Payments)
class  PaymentsAdmin(admin.ModelAdmin):
    list_display  = ["ref", 'amount', 'sub_account_ID', "email", "verified", "date_created"]
    list_filter = ["date_created", "verified"]
    search_fields = ["name", "ref" ]