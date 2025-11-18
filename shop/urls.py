from django.urls import path
from . import views
from django.conf import settings
from django.contrib.staticfiles.urls import static

urlpatterns = [
    path('', views.home, name="home"),
    path('register', views.register, name="register"),
    path('my-profile/<user>', views.profile, name="profile"),
    path('edit-user-address/<user>', views.edit_user_address, name="edit-user-address"),
    path('become-a-vendor', views.become_a_vendor, name="become-a-vendor"),
    path('vendor-profile/<user>', views.vendor_profile_page, name="vendor-profile"),
    path('list-product', views.list_product, name="list-product"),
    path('edit-list-product/<slug>', views.edit_list_product, name="edit-list-product"),
    path('products/<user>', views.vendor_all_products, name="vendor-products"),
    path('vendors', views.vendors, name="vendors-list"),
    path('vendor/<slug>', views.vendor_store, name="vendor-store"),
    path('vendor-messages/<slug>', views.vendor_messages, name="vendor-messages"),
    path('product-detail/<slug>', views.single_product, name="product-detail"),
    path('clear-notification/', views.clear_notification, name='clear_notification'),
    path('clear-notification-order/', views.clear_notification_order, name='clear_notification_order'),
    path('cart/<user>', views.cart, name='cart'),
    path('wishlist/<user>', views.wishlist, name='wishlist'),
    path('add-to-cart/<slug>', views.add_to_cart, name='add_to_cart'),
    path('add-to-wishlist/<slug>', views.add_to_wishlist, name='add-to-wishlist'),
    path('add-quantity/<slug>/<colour>/<size>', views.add_quantity, name='add-quantity'),
    path('reduce-quantity/<slug>/<colour>/<size>', views.reduce_quantity, name='reduce-quantity'),
    path('remove-from-cart/<slug>/<colour>/<size>', views.remove_from_cart, name='remove-from-cart'),
    path('remove-from-wishlist/<slug>', views.remove_from_wishlist, name='remove-from-wishlist'),
    path('clear-cart', views.clear_cart, name='clear-cart'),
    path('checkout/<user>', views.CheckOutView.as_view(), name='checkout'),
    path('user-orders/<user>', views.user_orders, name='user-orders'),
    path('user-orders-detail/<slug>/<ref_number>', views.order_details, name='user-orders-detail'),
    path('order-detail/<slug>/<ref_number>', views.vendor_view_order_details, name='order-detail'),
    path('payment/<slug>/<ref>', views.make_payment, name='payment'),
    path('thank-you', views.thank_you, name='thank-you'),
    path('orders-received/<vendor>', views.orders_received, name='orders-received'),
    path('verify-payment/<str:ref>/<slug>', views.verify_payment, name='verify_payment'),
    
]

urlpatterns +=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_URL)