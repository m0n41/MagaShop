from .models import Wishlist


def get_wishlist_product_ids(user):
    if not user.is_authenticated:
        return set()
    return set(Wishlist.objects.filter(user=user).values_list("product_id", flat=True))
