from django import template
from shop.models import Wishlist

register = template.Library()


@register.filter
def wishlist_item_count(user):
    if user.is_authenticated:
        qs = Wishlist.objects.filter(user=user, ordered=False)
        if qs.exists():
            wishlist = qs.count()
            return wishlist
    return 0