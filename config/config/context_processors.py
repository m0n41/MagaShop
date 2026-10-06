from django.urls import reverse
from catalog.models import Product
from cart.cart import Cart

def get_context_processoring(request):
    main_menu = {
        "Каталог": reverse("catalog:product_list"),
        "Контакты": reverse("pages:contacts"),
        "О нас": reverse("pages:about"),
    }
    return {"main_menu": main_menu}

def cart_context_processor(request):
    cart = Cart(request)
    return {
        "cart": cart
    }
    
def recent_views(request):
    recent_slugs = request.session.get("recent_views", [])
    recent_views = Product.objects.filter(slug__in=recent_slugs).select_related("category")
    return {
        "recent_views": recent_views,
    }