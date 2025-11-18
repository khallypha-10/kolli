from django import template
from shop.models import OrderItem

register = template.Library()


@register.filter
def cart_items(user):
    cart = None
    if user.is_authenticated:
        cart = OrderItem.objects.filter(user=user, ordered=False).order_by('-id')
    return cart


@register.filter
def cart_total(user):
    cart = None
    total = 0
    if user.is_authenticated:
        cart = OrderItem.objects.filter(user=user, ordered=False)
        
        for i in cart:
            quantity = i.quantity
            price = i.product.price
            discount = i.product.discount
            if discount:
                discounted_price = price - ((discount / 100) * price)
                prant = quantity * discounted_price
            else:
                prant = quantity * price
            total += prant
    return total