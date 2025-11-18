from django import template
from shop.models import Orders

register = template.Library()


@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        qs = Orders.objects.filter(user=user, ordered=False)
        if qs.exists():
            order = qs[0]
            return order.order_item.count()
    return 0

